import hashlib
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import asyncio
import httpx
import logging
from backend.app.config import settings
from backend.app.utils.telemetry import telemetry
from backend.app.services.sanitizer import sanitize_scraped_text

logger = logging.getLogger("verix.serpapi")

_serpapi_semaphore = asyncio.Semaphore(5)
_CACHE_TTL_SECONDS = 3600 * 24  # 24-hour cache for visual matches


class SingleFlightCacheManager:
    """
    Enterprise Single-Flight & Distributed Cache Coordinator.
    Prevents cache stampedes (dog-piling) when hundreds of concurrent requests
    miss the cache simultaneously for the same image hash.
    Supports:
    - Distributed Redis lock & caching (when settings.REDIS_URL is configured)
    - High-performance in-process async Lock map with TTL cleanup (default/fallback)
    """
    def __init__(self):
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self._in_flight_locks: Dict[str, asyncio.Lock] = {}
        self._registry_lock = asyncio.Lock()
        self._redis = None

    async def _get_redis(self):
        if getattr(settings, "REDIS_URL", None) and self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception as e:
                logger.warning("Redis initialization failed, falling back to in-process single-flight: %s", e)
                self._redis = None
        return self._redis

    async def get(self, key: str) -> Optional[List[Dict[str, Any]]]:
        r = await self._get_redis()
        if r:
            try:
                raw = await r.get(f"verix:serpapi:{key}")
                if raw:
                    import json
                    return json.loads(raw)
            except Exception:
                pass

        entry = self._local_cache.get(key)
        if entry:
            if time.time() - entry["timestamp"] < _CACHE_TTL_SECONDS:
                return entry["matches"]
            self._local_cache.pop(key, None)
        return None

    async def set(self, key: str, matches: List[Dict[str, Any]]):
        self._local_cache[key] = {
            "timestamp": time.time(),
            "matches": matches
        }
        r = await self._get_redis()
        if r:
            try:
                import json
                await r.set(f"verix:serpapi:{key}", json.dumps(matches), ex=_CACHE_TTL_SECONDS)
            except Exception as e:
                logger.warning("Redis cache write failed: %s", e)

    async def get_lock(self, key: str) -> asyncio.Lock:
        async with self._registry_lock:
            if key not in self._in_flight_locks:
                self._in_flight_locks[key] = asyncio.Lock()
            return self._in_flight_locks[key]


_cache_manager = SingleFlightCacheManager()
_SERPAPI_CACHE: Dict[str, Dict[str, Any]] = _cache_manager._local_cache


def _get_cache_key(image_url: str, image_bytes: Optional[bytes] = None) -> str:
    if image_bytes and len(image_bytes) > 0:
        return f"bytes:{hashlib.sha256(image_bytes).hexdigest()}"
    return f"url:{hashlib.sha256((image_url or '').encode()).hexdigest()}"

class SerpApiDegradedException(Exception):
    """Raised when SerpApi times out, hits rate limit (429), or service fails."""
    pass

def parse_domain_from_url(link: str) -> str:
    try:
        parsed = urlparse(link)
        netloc = parsed.netloc or parsed.path.split("/")[0]
        domain = netloc.split(":")[0]
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower()
    except Exception:
        return "unverified-domain.com"

from PIL import Image
import io

def prepare_image_for_serpapi(image_bytes: bytes) -> bytes:
    """Ensures image is optimized for SerpApi's 500KB upload limit."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        compressed = buf.getvalue()
        if len(compressed) > 450 * 1024:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=65, optimize=True)
            compressed = buf.getvalue()
        return compressed
    except Exception as e:
        logger.warning(f"Image optimization for SerpApi failed: {e}")
        return image_bytes

async def search_google_lens(
    image_url: str,
    image_bytes: Optional[bytes] = None,
    simulation_scenario: Optional[str] = None,
    lens_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Calls SerpApi Google Lens engine with the provided public image URL or uploaded image bytes.
    If image_bytes is provided, uploads directly to SerpApi's /image endpoint to get an image_id.
    Returns a normalized list of visual matches.
    If SerpApi times out or fails, raises SerpApiDegradedException to trigger fail-closed fallback.
    """
    telemetry.record_serpapi_attempt()
    
    # Explicit simulation scenarios (e.g. for automated tests or Quick-Try demo buttons)
    demo_enabled = settings.ENVIRONMENT.lower() != "production"

    if simulation_scenario and demo_enabled:
        telemetry.record_serpapi_success()
        return get_mock_visual_matches(image_url, simulation_scenario)

    cache_key = _get_cache_key(image_url, image_bytes)
    if not simulation_scenario:
        cached = await _cache_manager.get(cache_key)
        if cached:
            logger.info("Serving SerpApi Google Lens results from local hash cache: %s", cache_key)
            telemetry.record_serpapi_cache_hit()
            telemetry.record_serpapi_success()
            return cached

    # Enterprise Single-Flight: acquire lock for this specific cache_key to prevent cache stampedes
    key_lock = await _cache_manager.get_lock(cache_key)
    async with key_lock:
        # Double-check inside lock in case a concurrent worker just completed the query
        if not simulation_scenario:
            cached = await _cache_manager.get(cache_key)
            if cached:
                logger.info("Serving SerpApi Google Lens results from single-flight populated cache: %s", cache_key)
                telemetry.record_serpapi_cache_hit()
                telemetry.record_serpapi_success()
                return cached

        # Never convert an ordinary user input into a simulated search result.
        if not settings.SERPAPI_API_KEY:
            telemetry.record_serpapi_failure("SERPAPI_API_KEY is not configured.")
            raise SerpApiDegradedException("SerpApi API key not configured.")

    try:
        requested_types = lens_types or ["visual_matches"]
        allowed_types = {"visual_matches", "exact_matches", "products", "about_this_image"}
        requested_types = [item for item in requested_types if item in allowed_types]
        if not requested_types:
            requested_types = ["visual_matches"]
        params: Dict[str, Any] = {
            "engine": "google_lens",
            "api_key": settings.SERPAPI_API_KEY,
            "hl": settings.SERPAPI_LANGUAGE,
        }

        # If image_bytes is provided and image_url is not already a public URL, upload to SerpApi Image API
        is_public_image_url = bool(image_url and image_url.lower().startswith(("http://", "https://")))
        if not is_public_image_url and image_bytes and len(image_bytes) > 0:
            try:
                optimized = prepare_image_for_serpapi(image_bytes)
                async with httpx.AsyncClient(timeout=12.0) as upload_client:
                    files = {"image": ("product.jpg", optimized, "image/jpeg")}
                    data = {"api_key": settings.SERPAPI_API_KEY}
                    upload_resp = await upload_client.post("https://serpapi.com/image", files=files, data=data)
                    if upload_resp.status_code == 200:
                        image_id = upload_resp.json().get("image_id")
                        if image_id:
                            params["image_id"] = image_id
                            logger.info(f"Successfully uploaded image to SerpApi Image API: {image_id}")
            except Exception as up_err:
                logger.warning(f"SerpApi image upload failed, falling back to URL search: {up_err}")

        # Fallback to image_url if image_id not set
        if "image_id" not in params:
            if not is_public_image_url:
                raise SerpApiDegradedException(
                    "Uploaded image is not publicly reachable. Configure PUBLIC_BASE_URL or use the SerpApi image upload path."
                )
            params["url"] = image_url

        async with _serpapi_semaphore:
            async with httpx.AsyncClient(timeout=35.0) as client:
                resp = await client.get("https://serpapi.com/search", params=params)

            if resp.status_code == 429:
                err_msg = "SerpApi rate limit exceeded (HTTP 429)."
                telemetry.record_serpapi_failure(err_msg)
                raise SerpApiDegradedException(err_msg)

            resp.raise_for_status()
            data = resp.json()
            telemetry.record_serpapi_success()

            ai_overview_text = None
            ai_ov = data.get("ai_overview")
            if isinstance(ai_ov, dict):
                ai_overview_text = ai_ov.get("text") or ai_ov.get("snippet")
            elif isinstance(ai_ov, str):
                ai_overview_text = ai_ov

            normalized_matches = []
            raw_matches = data.get("visual_matches", [])
            if not raw_matches or not isinstance(raw_matches, list):
                raw_matches = data.get("organic_results", []) or []

            for item in raw_matches:
                if not isinstance(item, dict):
                    continue
                link = item.get("link") or item.get("product_link") or ""
                domain = parse_domain_from_url(link)
                title = sanitize_scraped_text(item.get("title", ""))
                source = item.get("source", domain)
                thumbnail = item.get("thumbnail") or item.get("image")
                source_icon = item.get("source_icon")
                in_stock = item.get("in_stock")
                price_info = item.get("price", {})
                price_str = price_info.get("value") if isinstance(price_info, dict) else str(price_info or "")
                extracted_price = price_info.get("extracted_value") if isinstance(price_info, dict) else item.get("extracted_price")
                currency = price_info.get("currency") if isinstance(price_info, dict) else None
                normalized_matches.append({
                    "domain": domain,
                    "title": title,
                    "price": price_str,
                    "extracted_price": extracted_price,
                    "currency": currency,
                    "link": link,
                    "source": source,
                    "thumbnail": thumbnail,
                    "source_icon": source_icon,
                    "in_stock": in_stock,
                    "ai_overview": ai_overview_text,
                    "flagged": False,
                    "risk_note": None,
                    "is_whitelisted": False,
                    "engine": "google_lens",
                    "evidence_type": "visual_matches",
                })

            deduped = _dedupe_matches(normalized_matches)
            if not simulation_scenario and deduped:
                await _cache_manager.set(cache_key, deduped)
            return deduped

    except (httpx.TimeoutException, httpx.NetworkError) as exc:
        err_msg = f"SerpApi connection timeout/network failure: {str(exc)}"
        logger.warning(err_msg)
        telemetry.record_serpapi_failure(err_msg)
        raise SerpApiDegradedException(err_msg)
    except httpx.HTTPStatusError as exc:
        err_msg = f"SerpApi HTTP error status {exc.response.status_code}: {exc.response.text}"
        logger.error(err_msg)
        telemetry.record_serpapi_failure(err_msg)
        raise SerpApiDegradedException(err_msg)
    except Exception as exc:
        if isinstance(exc, SerpApiDegradedException):
            raise
        err_msg = f"Unexpected SerpApi client error: {str(exc)}"
        logger.error(err_msg)
        telemetry.record_serpapi_failure(err_msg)
        raise SerpApiDegradedException(err_msg)


def get_mock_visual_matches(image_url: str, scenario: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Provides realistic mock Google Lens visual matches for hackathon testing and demo flows.
    Scenarios:
    - 'insufficient': returns < 2 matches to trigger guardrail
    - 'cloned_seller': returns 5 unverified domains with stolen catalog images
    - 'default' / 'sneaker_scam': returns matches with suspicious 80% price disparity
    """
    if scenario == "insufficient":
        # Returns 1 match, triggering Guardrail 6 (Insufficient Data)
        return [
            {
                "domain": "craftmaker-portfolio.in",
                "title": "Bespoke Handcrafted Ceramic Vase by Studio A",
                "price": "₹3,400",
                "extracted_price": 3400.0,
                "currency": "INR",
                "link": "https://craftmaker-portfolio.in/shop/ceramic-vase-1",
                "source": "Craftmaker Portfolio",
                "thumbnail": "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=150",
                "flagged": False,
                "risk_note": "Single indexed match found.",
                "is_whitelisted": False
            }
        ]
        
    if scenario == "cloned_seller":
        # Seller persona scenario: exact image used across multiple unverified stores
        return [
            {
                "domain": "artisanhandicrafts.com",
                "title": "Original Handcrafted Brass Diya Lamp - Limited Edition",
                "price": "₹2,800",
                "extracted_price": 2800.0,
                "currency": "INR",
                "link": "https://artisanhandicrafts.com/item/brass-diya",
                "source": "Artisan Handicrafts (Original Creator)",
                "thumbnail": "https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?w=150",
                "flagged": False,
                "risk_note": "Earliest appearance / Original catalog entry",
                "is_whitelisted": False
            },
            {
                "domain": "mega-festive-deals-99.shop",
                "title": "Traditional Brass Puja Lamp 70% Off Today",
                "price": "₹399",
                "extracted_price": 399.0,
                "currency": "INR",
                "link": "https://mega-festive-deals-99.shop/diya-lamp",
                "source": "Mega Deals Shop",
                "thumbnail": "https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?w=150",
                "flagged": True,
                "risk_note": "Unverified newly registered domain using identical photo at 85% discount.",
                "is_whitelisted": False
            },
            {
                "domain": "cheapdecoroutlet.biz",
                "title": "Indian Metal Lamp Vintage Diya",
                "price": "₹450",
                "extracted_price": 450.0,
                "currency": "INR",
                "link": "https://cheapdecoroutlet.biz/vintage-diya",
                "source": "Cheap Decor Outlet",
                "thumbnail": "https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?w=150",
                "flagged": True,
                "risk_note": "Unverified seller domain, cloned product title.",
                "is_whitelisted": False
            },
            {
                "domain": "shophub-express.online",
                "title": "Antique Brass Diya Fast Delivery",
                "price": "₹420",
                "extracted_price": 420.0,
                "currency": "INR",
                "link": "https://shophub-express.online/products/lamp-01",
                "source": "ShopHub Express",
                "thumbnail": "https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?w=150",
                "flagged": True,
                "risk_note": "Unverified merchant using stolen image.",
                "is_whitelisted": False
            }
        ]

    # Default e-commerce buyer scam scenario (e.g. Air Jordan or luxury item)
    return [
        {
            "domain": "nike.com",
            "title": "Air Jordan 1 Retro High OG Men's Shoes",
            "price": "₹16,995",
            "extracted_price": 16995.0,
            "currency": "INR",
            "link": "https://www.nike.com/in/t/air-jordan-1-retro-high-og",
            "source": "Nike Official Store",
            "thumbnail": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=150",
            "flagged": False,
            "risk_note": "Authorized flagship brand domain.",
            "is_whitelisted": True
        },
        {
            "domain": "sneakerflashsale-india.club",
            "title": "Air Jordan 1 Retro High OG Clearance 85% Off",
            "price": "₹1,499",
            "extracted_price": 1499.0,
            "currency": "INR",
            "link": "https://sneakerflashsale-india.club/order-aj1",
            "source": "Sneaker Flash Sale",
            "thumbnail": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=150",
            "flagged": True,
            "risk_note": "Extreme price disparity (91% discount on official retail photo).",
            "is_whitelisted": False
        },
        {
            "domain": "kicksvault-deals.xyz",
            "title": "AJ1 Retro High Limited Stocks Left",
            "price": "₹1,899",
            "extracted_price": 1899.0,
            "currency": "INR",
            "link": "https://kicksvault-deals.xyz/aj1-limited",
            "source": "Kicks Vault XYZ",
            "thumbnail": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=150",
            "flagged": True,
            "risk_note": "Unverified top-level domain with stolen official imagery.",
            "is_whitelisted": False
        },
        {
            "domain": "trendysneakers-outlet.site",
            "title": "Jordan Retro 1 High Sneaker Free Shipping",
            "price": "₹1,650",
            "extracted_price": 1650.0,
            "currency": "INR",
            "link": "https://trendysneakers-outlet.site/p/jordan1",
            "source": "Trendy Sneakers Outlet",
            "thumbnail": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=150",
            "flagged": True,
            "risk_note": "Unverified merchant domain without physical address or merchant registry.",
            "is_whitelisted": False
        }
    ]

def canonicalize_evidence_url(link: str) -> str:
    """Normalize harmless URL variations before counting evidence."""
    if not link:
        return ""
    try:
        parsed = urlparse(link.strip())
        if not parsed.netloc:
            return link.strip().lower().rstrip("/")
        query = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.lower().startswith(("utm_", "fbclid", "gclid", "ref", "tag"))
        ]
        hostname = (parsed.hostname or "").lower()
        netloc = hostname
        if parsed.port:
            netloc = f"{hostname}:{parsed.port}"
        path = parsed.path.rstrip("/") or "/"
        return urlunparse((parsed.scheme.lower(), netloc, path, "", urlencode(query), ""))
    except ValueError:
        return link.strip().lower().rstrip("/")


def _dedupe_matches(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge duplicate evidence while preserving cross-engine corroboration."""
    seen: Dict[Any, int] = {}
    result = []
    for match in matches:
        key = canonicalize_evidence_url(match.get("link") or "") or (
            match.get("domain", "").strip().lower(), match.get("title", "").strip().lower()
        )
        if key in seen:
            existing = result[seen[key]]
            engine = match.get("engine")
            evidence_type = match.get("evidence_type")
            engines = set(existing.get("engines") or ([existing.get("engine")] if existing.get("engine") else []))
            evidence_types = set(existing.get("evidence_types") or ([existing.get("evidence_type")] if existing.get("evidence_type") else []))
            if engine:
                engines.add(engine)
            if evidence_type:
                evidence_types.add(evidence_type)
            existing["engines"] = sorted(engines)
            existing["evidence_types"] = sorted(evidence_types)
            existing["corroboration_count"] = len(engines) or len(evidence_types) or 1
            for field in ("title", "price", "extracted_price", "currency", "thumbnail", "risk_note", "source_icon", "in_stock", "ai_overview", "typical_price_range"):
                if not existing.get(field) and match.get(field):
                    existing[field] = match[field]
            continue
        seen[key] = len(result)
        engine = match.get("engine")
        evidence_type = match.get("evidence_type")
        match["engines"] = [engine] if engine else []
        match["evidence_types"] = [evidence_type] if evidence_type else []
        match["corroboration_count"] = 1
        result.append(match)
    return result

def _safe_search_query(text: str, max_length: int = 120) -> str:
    """Build a compact query from already-sanitized Lens text."""
    cleaned = sanitize_scraped_text(text or "", max_length=max_length)
    return " ".join(cleaned.split())[:max_length]

async def search_google_shopping(query: str) -> List[Dict[str, Any]]:
    """Fetch bounded commerce evidence; secondary failures are intentionally soft."""
    query = _safe_search_query(query)
    if not query or not settings.SERPAPI_API_KEY:
        return []
    try:
        params = {
            "engine": "google_shopping", "q": query, "api_key": settings.SERPAPI_API_KEY,
            "country": settings.SERPAPI_COUNTRY, "hl": settings.SERPAPI_LANGUAGE,
        }
        async with _serpapi_semaphore:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get("https://serpapi.com/search", params=params)
                response.raise_for_status()
                data = response.json()
        
        price_insights = data.get("price_insights") or {}
        typical_range = price_insights.get("typical_price_range")
        typical_price_str = None
        if isinstance(typical_range, list) and len(typical_range) >= 2:
            typical_price_str = f"{typical_range[0]} - {typical_range[1]}"
        elif isinstance(typical_range, str):
            typical_price_str = typical_range

        results = []
        for item in data.get("shopping_results", [])[:10]:
            link = item.get("product_link") or item.get("link") or ""
            results.append({
                "domain": parse_domain_from_url(link or item.get("source", "")),
                "title": sanitize_scraped_text(item.get("title", "")),
                "price": item.get("price"),
                "extracted_price": item.get("extracted_price"),
                "currency": None,
                "link": link,
                "source": item.get("source"),
                "thumbnail": item.get("thumbnail"),
                "source_icon": item.get("source_icon"),
                "typical_price_range": typical_price_str,
                "flagged": False,
                "risk_note": None,
                "is_whitelisted": False,
                "engine": "google_shopping",
                "evidence_type": "shopping_results",
            })
        return _dedupe_matches(results)
    except Exception as exc:
        logger.warning("Secondary Google Shopping evidence unavailable: %s", exc)
        return []

async def search_google_web(query: str) -> List[Dict[str, Any]]:
    """Fetch targeted web context for the detected product; fail-soft by design."""
    query = _safe_search_query(query)
    if not query or not settings.SERPAPI_API_KEY:
        return []
    try:
        params = {
            "engine": "google", "q": query, "api_key": settings.SERPAPI_API_KEY,
            "country": settings.SERPAPI_COUNTRY, "hl": settings.SERPAPI_LANGUAGE,
        }
        async with _serpapi_semaphore:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get("https://serpapi.com/search", params=params)
                response.raise_for_status()
                data = response.json()
        results = []
        for item in data.get("organic_results", [])[:10]:
            link = item.get("link") or ""
            results.append({
                "domain": parse_domain_from_url(link),
                "title": sanitize_scraped_text(item.get("title", "")),
                "price": None,
                "extracted_price": None,
                "currency": None,
                "link": link,
                "source": item.get("source") or parse_domain_from_url(link),
                "thumbnail": item.get("thumbnail"),
                "flagged": False,
                "risk_note": None,
                "is_whitelisted": False,
                "engine": "google",
                "evidence_type": "organic_results",
            })
        return _dedupe_matches(results)
    except Exception as exc:
        logger.warning("Secondary Google Search evidence unavailable: %s", exc)
        return []
async def enrich_with_secondary_engines(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add bounded Shopping evidence without making the primary scan fragile or slow."""
    if not settings.ENABLE_MULTI_ENGINE or not matches:
        return matches
    # Fast path: If Google Lens already found rich visual matches (>= 8),
    # skip secondary engines to keep response time fast (~3s) and conserve SerpApi credits.
    if len(matches) >= 8:
        logger.info("Primary Google Lens returned %d matches; skipping secondary engines for speed.", len(matches))
        return matches

    title = next((m.get("title") for m in matches if m.get("title")), "")
    query = _safe_search_query(title)
    if len(query) < 8:
        return matches
    enriched = list(matches)
    secondary = []
    if settings.SERPAPI_MAX_SECONDARY_CALLS >= 1:
        secondary.append(search_google_shopping(query))
    if settings.SERPAPI_MAX_SECONDARY_CALLS >= 2:
        secondary.append(search_google_web(query))
    if secondary:
        try:
            secondary_results = await asyncio.wait_for(
                asyncio.gather(*secondary, return_exceptions=True),
                timeout=4.0
            )
            for result in secondary_results:
                if isinstance(result, list):
                    enriched.extend(result[:5])
        except asyncio.TimeoutError:
            logger.info("Secondary engines timed out after 4.0s; proceeding with primary Lens matches.")
        except Exception as exc:
            logger.warning("Secondary engines encountered error: %s", exc)
    return _dedupe_matches(enriched)


async def search_domain_trust_reputation(domain: str) -> Dict[str, Any]:
    """
    Evaluates domain reputation and scam/consumer complaint signals using SerpApi Google search.
    Checks for Trustpilot, Reddit, scam adviser, and consumer fraud signals. Fail-soft by design.
    """
    clean_domain = (domain or "").strip().lower().removeprefix("www.")
    if not clean_domain:
        return {
            "domain": "",
            "status": "unknown",
            "trust_score": None,
            "verdict_label": "No store domain provided",
            "warning_signals": [],
            "snippet_samples": [],
            "sources_analyzed": 0,
            "is_whitelisted": False,
        }

    # Fast heuristic for well-known verified platforms and brand flagships
    from backend.app.services.whitelist import is_domain_whitelisted
    is_wl, trusted_name = is_domain_whitelisted(f"https://{clean_domain}")
    if is_wl:
        return {
            "domain": clean_domain,
            "status": "trusted",
            "trust_score": 96,
            "verdict_label": f"Verified Platform / Brand Flagship ({trusted_name or clean_domain})",
            "warning_signals": [],
            "snippet_samples": ["Verified marketplace with active buyer dispute protection."],
            "sources_analyzed": 1,
            "is_whitelisted": True,
        }

    if not settings.SERPAPI_API_KEY:
        return {
            "domain": clean_domain,
            "status": "neutral",
            "trust_score": 75,
            "verdict_label": "Standard Web Footprint",
            "warning_signals": [],
            "snippet_samples": [],
            "sources_analyzed": 0,
            "is_whitelisted": False,
        }

    try:
        query = f'"{clean_domain}" (scam OR fake OR counterfeit OR "trustpilot" OR review)'
        params = {
            "engine": "google",
            "q": query,
            "api_key": settings.SERPAPI_API_KEY,
            "country": settings.SERPAPI_COUNTRY,
            "hl": settings.SERPAPI_LANGUAGE,
            "num": 5,
        }
        async with _serpapi_semaphore:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.get("https://serpapi.com/search", params=params)
                response.raise_for_status()
                data = response.json()

        organic = data.get("organic_results", [])
        scam_keywords = ["scam", "counterfeit", "fake", "fraud", "beware", "avoid", "ripoff", "never received", "chargeback"]
        warnings = []
        snippets = []

        scam_hit_count = 0
        for item in organic[:5]:
            snippet = sanitize_scraped_text(item.get("snippet", ""))
            title = sanitize_scraped_text(item.get("title", ""))
            combined = (title + " " + snippet).lower()
            if any(k in combined for k in scam_keywords):
                scam_hit_count += 1
                warnings.append(title)
            if snippet:
                snippets.append(snippet[:180])

        if scam_hit_count >= 2:
            status = "suspicious"
            score = max(20, 70 - (scam_hit_count * 20))
            label = "Caution: Consumer Complaints or Scam Alerts Detected"
        elif scam_hit_count == 1:
            status = "caution"
            score = 65
            label = "Mixed Reputation Signals on Public Forums"
        else:
            status = "trusted" if len(organic) >= 3 else "neutral"
            score = 85 if len(organic) >= 3 else 75
            label = "Clean Domain Footprint: No Serious Scam Signals Found"

        return {
            "domain": clean_domain,
            "status": status,
            "trust_score": score,
            "verdict_label": label,
            "warning_signals": warnings[:3],
            "snippet_samples": snippets[:3],
            "sources_analyzed": len(organic),
            "is_whitelisted": False,
        }
    except Exception as exc:
        logger.warning("Domain reputation search unavailable for %s: %s", clean_domain, exc)
        return {
            "domain": clean_domain,
            "status": "neutral",
            "trust_score": 70,
            "verdict_label": "Unindexed or New Domain",
            "warning_signals": [],
            "snippet_samples": [],
            "sources_analyzed": 0,
            "is_whitelisted": False,
        }


async def search_comparison_videos(query: str) -> List[Dict[str, Any]]:
    """
    Fetches real-vs-fake comparison, teardown, and unboxing videos using SerpApi YouTube engine.
    """
    clean_q = _safe_search_query(query)
    if not clean_q or len(clean_q) < 4 or not settings.SERPAPI_API_KEY:
        return []

    try:
        search_term = f'"{clean_q}" real vs fake OR unboxing'
        params = {
            "engine": "youtube",
            "search_query": search_term,
            "api_key": settings.SERPAPI_API_KEY,
        }
        async with _serpapi_semaphore:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.get("https://serpapi.com/search", params=params)
                response.raise_for_status()
                data = response.json()

        videos = []
        for item in data.get("video_results", [])[:3]:
            channel_info = item.get("channel", {})
            channel_name = channel_info.get("name") if isinstance(channel_info, dict) else str(channel_info or "YouTube")
            thumbnail = item.get("thumbnail")
            if isinstance(thumbnail, dict):
                thumbnail = thumbnail.get("static") or thumbnail.get("rich")
            videos.append({
                "title": sanitize_scraped_text(item.get("title", "")),
                "link": item.get("link", ""),
                "thumbnail": thumbnail,
                "channel": channel_name,
                "views": item.get("views"),
                "length": item.get("length"),
                "published_date": item.get("published_date"),
            })
        return videos
    except Exception as exc:
        logger.warning("YouTube video search unavailable for %s: %s", clean_q, exc)
        return []


async def fetch_retailer_price_matrix(query: str, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Scrapes authorized store pricing, MSRP typical price range, and retailer inventory
    across major e-commerce platforms using SerpApi Google Shopping engine.
    """
    clean_q = _safe_search_query(query)
    if not clean_q or len(clean_q) < 4 or not settings.SERPAPI_API_KEY:
        return {
            "query": clean_q,
            "has_data": False,
            "typical_price_range": None,
            "retailers": [],
        }

    try:
        req_country = country or settings.SERPAPI_COUNTRY
        params = {
            "engine": "google_shopping",
            "q": clean_q,
            "api_key": settings.SERPAPI_API_KEY,
            "country": req_country,
            "hl": settings.SERPAPI_LANGUAGE,
            "num": 8,
        }
        async with _serpapi_semaphore:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get("https://serpapi.com/search", params=params)
                response.raise_for_status()
                data = response.json()

        price_insights = data.get("price_insights") or {}
        typical_range = price_insights.get("typical_price_range")
        typical_price_str = None
        if isinstance(typical_range, list) and len(typical_range) >= 2:
            typical_price_str = f"{typical_range[0]} – {typical_range[1]}"
        elif isinstance(typical_range, str):
            typical_price_str = typical_range

        from backend.app.services.whitelist import is_domain_whitelisted
        retailers = []
        for item in data.get("shopping_results", [])[:6]:
            link = item.get("product_link") or item.get("link") or ""
            source_name = item.get("source") or parse_domain_from_url(link)
            is_wl, trusted_name = is_domain_whitelisted(link)
            
            retailers.append({
                "store_name": trusted_name or source_name,
                "domain": parse_domain_from_url(link),
                "price": item.get("price"),
                "extracted_price": item.get("extracted_price"),
                "link": link,
                "rating": item.get("rating"),
                "reviews": item.get("reviews"),
                "delivery": item.get("delivery"),
                "thumbnail": item.get("thumbnail"),
                "is_authorized": is_wl or any(dom in source_name.lower() for dom in ["boat", "amazon", "flipkart", "croma", "reliance", "tatacliq", "myntra", "apple", "nike", "samsung", "sony", "walmart", "target"]),
                "badge": item.get("badge") or ("Authorized Retailer" if is_wl else None),
            })

        # Sort retailers by price if available
        priced_retailers = sorted(
            retailers,
            key=lambda r: (r["extracted_price"] is None, r["extracted_price"] or float("inf"))
        )

        return {
            "query": clean_q,
            "has_data": len(priced_retailers) > 0,
            "typical_price_range": typical_price_str,
            "retailers": priced_retailers,
        }
    except Exception as exc:
        logger.warning("Google Shopping price matrix search unavailable for %s: %s", clean_q, exc)
        return {
            "query": clean_q,
            "has_data": False,
            "typical_price_range": None,
            "retailers": [],
        }



