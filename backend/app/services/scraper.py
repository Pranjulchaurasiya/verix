"""Web scraper for extracting primary product image from listing URLs."""

import json
from urllib.parse import urljoin, urlparse
import ipaddress
import socket
import httpx
from bs4 import BeautifulSoup
from typing import Tuple, Optional
import logging

logger = logging.getLogger("verix.scraper")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

def _validate_public_url(raw_url: str) -> str:
    """Reject non-HTTP and private-network URLs to prevent SSRF."""
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only public HTTP(S) URLs are supported.")
    hostname = parsed.hostname
    if hostname.lower() in {"localhost", "localhost.localdomain"}:
        raise ValueError("Private or local URLs are not supported.")
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(hostname, None)}
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                raise ValueError("Private or local URLs are not supported.")
    except socket.gaierror as exc:
        raise ValueError("The URL host could not be resolved.") from exc
    return raw_url

async def _get_limited(client: httpx.AsyncClient, url: str, max_bytes: int = 15 * 1024 * 1024) -> httpx.Response:
    current_url = url
    for _ in range(4):
        _validate_public_url(current_url)
        async with client.stream("GET", current_url, follow_redirects=False) as response:
            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                if not location:
                    raise ValueError("Remote resource redirected without a destination.")
                current_url = urljoin(str(response.url), location)
                _validate_public_url(current_url)
                continue
            response.raise_for_status()
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > max_bytes:
                raise ValueError("Remote resource exceeds the maximum image size.")
            chunks = []
            total = 0
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("Remote resource exceeds the maximum image size.")
                chunks.append(chunk)
            response._content = b"".join(chunks)
            return response
    raise ValueError("Remote resource exceeded the redirect limit.")

SCRAPER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

import io
import re
from PIL import Image


EXCLUDED_IMAGE_KEYWORDS = [
    "fls-eu", "uedata", "pixel", "beacon", "tracking", "transparent",
    "spacer", "1x1", "blank", "sprite", "logo", "icon", "badge",
    "avatar", "analytics", "doubleclick", "bat.bing", "adsystem",
    "facebook.com/tr", "data:image/", "grey-pixel", "clear.gif"
]

def _is_tracking_or_icon_url(url_str: str) -> bool:
    lower = url_str.lower()
    return any(kw in lower for kw in EXCLUDED_IMAGE_KEYWORDS)

async def _resolve_amazon_asin_image(target_url: str) -> Optional[Tuple[bytes, str, str]]:
    # If this is an Amazon shortlink (e.g. amzn.in/d/..., amzn.to/...), resolve the redirect first
    if any(dom in target_url.lower() for dom in ["amzn.in", "amzn.to", "amzn.asia"]):
        try:
            async with httpx.AsyncClient(timeout=6.0, headers=SCRAPER_HEADERS, follow_redirects=True) as red_client:
                r = await red_client.get(target_url)
                if r.status_code < 400 and str(r.url) != target_url:
                    target_url = str(r.url)
        except Exception:
            pass

    asin_match = re.search(
        r'(?:/dp/|/gp/product/|/gp/aw/d/|/d/|/product/|/gp/offer-listing/|[?&]asin=)([A-Z0-9]{10})',
        target_url,
        re.IGNORECASE
    )
    if not (asin_match and any(dom in target_url.lower() for dom in ["amazon.", "amzn."])):
        return None
    asin = asin_match.group(1).upper()
    amazon_cdn_urls = [
        f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01.MAIN._SCRM_.jpg",
        f"https://m.media-amazon.com/images/P/{asin}.01._SCLZZZZZZZ_SX500_.jpg",
    ]
    async with httpx.AsyncClient(timeout=8.0, headers=SCRAPER_HEADERS) as cdn_client:
        for c_url in amazon_cdn_urls:
            try:
                c_resp = await cdn_client.get(c_url, follow_redirects=True)
                if c_resp.status_code == 200 and len(c_resp.content) > 2000:
                    with Image.open(io.BytesIO(c_resp.content)) as c_img:
                        if c_img.size[0] >= 100 and c_img.size[1] >= 100:
                            logger.info("Found official Amazon ASIN CDN high-res image for %s: %s", asin, c_url)
                            return c_resp.content, c_url, asin
            except Exception as exc:
                logger.debug("Amazon CDN candidate failed for %s: %s", c_url, exc)
    return None

async def extract_product_image_from_url(url: str) -> Tuple[bytes, str, Optional[str], str]:
    """
    Fetches the URL. If it's directly an image, downloads and validates it.
    If it's an HTML page, parses metadata and DOM to extract the primary high-res product photo.
    Filters out 1x1 telemetry beacons (e.g. uedata, transparent-pixel) and validates raster dimensions.
    Returns: (image_bytes, resolved_image_url, page_title, availability)
    """
    _validate_public_url(url)
    
    # 0. Pre-emptively detect Amazon ASIN for canonical high-res product photography
    amazon_cdn_payload = await _resolve_amazon_asin_image(url)

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=False, headers=SCRAPER_HEADERS) as client:
        try:
            resp = await _get_limited(client, url)
            _validate_public_url(str(resp.url))
            if not amazon_cdn_payload:
                amazon_cdn_payload = await _resolve_amazon_asin_image(str(resp.url))
        except Exception as fetch_exc:
            # If the remote storefront blocked scraping (e.g. anti-bot 503) but we have the ASIN image, use it!
            if amazon_cdn_payload:
                return amazon_cdn_payload[0], amazon_cdn_payload[1], f"Amazon Product ({amazon_cdn_payload[2]})", "unknown"
            raise fetch_exc
        
        content_type = resp.headers.get("content-type", "").lower()
        
        # If the URL is already an image
        if "image/" in content_type:
            try:
                with Image.open(io.BytesIO(resp.content)) as pil_img:
                    if pil_img.size[0] >= 40 and pil_img.size[1] >= 40:
                        return resp.content, str(resp.url), None, "unknown"
            except Exception:
                pass
            
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
        
        page_title = None
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()

        availability = "unknown"
        page_text = soup.get_text(" ", strip=True).lower()
        availability_patterns = {
            "discontinued": ("discontinued", "no longer available", "product has been discontinued"),
            "out_of_stock": ("out of stock", "currently unavailable", "temporarily unavailable", "sold out"),
            "in_stock": ("in stock", "available now", "add to cart", "buy now"),
        }
        for status, markers in availability_patterns.items():
            if any(marker in page_text for marker in markers):
                availability = status
                break

        # Candidate accumulation list in priority order
        candidates = []
        if amazon_cdn_payload:
            candidates.append(amazon_cdn_payload[1])

        # 1. Amazon-specific high-resolution selectors
        landing_img = soup.find("img", id="landingImage") or soup.find("img", id="imgBlkFront") or soup.find("img", id="main-image")
        if landing_img:
            # Check dynamic JSON images attribute
            dyn_attr = landing_img.get("data-a-dynamic-image")
            if dyn_attr:
                try:
                    dyn_dict = json.loads(dyn_attr)
                    # Sort keys by highest pixel resolution
                    sorted_urls = sorted(
                        dyn_dict.keys(),
                        key=lambda k: dyn_dict[k][0] * dyn_dict[k][1] if isinstance(dyn_dict[k], list) and len(dyn_dict[k]) >= 2 else 0,
                        reverse=True
                    )
                    candidates.extend(sorted_urls)
                except Exception:
                    pass
            if landing_img.get("data-old-hires"):
                candidates.append(landing_img["data-old-hires"])
            if landing_img.get("src"):
                candidates.append(landing_img["src"])

        # 2. OpenGraph / Twitter meta tags
        og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if og_img and og_img.get("content"):
            candidates.append(og_img["content"])
            
        tw_img = soup.find("meta", attrs={"name": "twitter:image"})
        if tw_img and tw_img.get("content"):
            candidates.append(tw_img["content"])
                
        # 3. JSON-LD schema.org Product
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                if not script.string:
                    continue
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") in ("Product", "ItemPage", "IndividualProduct"):
                        offers = item.get("offers")
                        offer_items = offers if isinstance(offers, list) else [offers]
                        for offer in offer_items:
                            if isinstance(offer, dict):
                                offer_status = str(offer.get("availability", "")).lower()
                                if "discontinued" in offer_status:
                                    availability = "discontinued"
                                elif "outofstock" in offer_status or "soldout" in offer_status:
                                    availability = "out_of_stock"
                                elif "instock" in offer_status:
                                    availability = "in_stock"
                        img = item.get("image")
                        if isinstance(img, str):
                            candidates.append(img)
                        elif isinstance(img, list):
                            for entry in img:
                                if isinstance(entry, str):
                                    candidates.append(entry)
                        elif isinstance(img, dict) and img.get("url"):
                            candidates.append(img["url"])
            except Exception:
                continue

        # 4. Filtered DOM <img> tags
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-original") or img.get("data-zoom-image")
            if src and not _is_tracking_or_icon_url(src):
                candidates.append(src)

        # 5. Evaluate candidates in order, rejecting tracking pixels or microscopic icons
        for cand_url in candidates:
            if not cand_url or _is_tracking_or_icon_url(cand_url):
                continue
            resolved_url = urljoin(str(resp.url), cand_url)
            try:
                _validate_public_url(resolved_url)
                img_resp = await _get_limited(client, resolved_url)
                _validate_public_url(str(img_resp.url))
                
                # Check raster dimensions using PIL
                with Image.open(io.BytesIO(img_resp.content)) as pil_img:
                    w, h = pil_img.size
                    # Require minimum 60x60 dimensions and at least 500 bytes
                    if w >= 60 and h >= 60 and len(img_resp.content) >= 500:
                        return img_resp.content, resolved_url, page_title, availability
                    else:
                        logger.debug("Discarding micro-image / beacon: %s (%dx%d, %d bytes)", resolved_url, w, h, len(img_resp.content))
            except Exception as exc:
                logger.debug("Failed evaluating candidate %s: %s", cand_url, exc)
                continue

        # 6. Fallback to pre-fetched Amazon CDN image if available
        if amazon_cdn_payload:
            return amazon_cdn_payload[0], amazon_cdn_payload[1], page_title, availability

        raise ValueError("No valid product image could be detected on the provided webpage URL.")

