"""Source-limited evidence assessment with optional experimental LLM output."""

import json
import asyncio
from typing import List, Dict, Any, Optional
import logging
import httpx
from pydantic import BaseModel, Field
from groq import AsyncGroq
from backend.app.config import settings
from backend.app.services.sanitizer import sanitize_banned_words, sanitize_matched_domains
from backend.app.services.whitelist import is_domain_whitelisted

logger = logging.getLogger("verix.ai_evaluator")

_gemini_semaphore = asyncio.Semaphore(3)

class GeminiFlaggedDomain(BaseModel):
    domain: str
    flagged: bool = False
    risk_note: Optional[str] = None

class GeminiVerdictSchema(BaseModel):
    trust_score: int = Field(50, ge=0, le=100)
    confidence: str = Field("medium", pattern="^(low|medium|high)$")
    explanation: str
    risk_category: str = Field("moderate_risk", pattern="^(trusted|low_risk|moderate_risk|high_risk)$")
    action_recommendation: str
    flagged_domains: List[GeminiFlaggedDomain] = []

def is_valid_api_key(key: Optional[str]) -> bool:
    if not key:
        return False
    k = key.strip()
    if not k or k in ("your_gemini_key_here", "your_groq_key_here", "none", "null"):
        return False
    return len(k) > 10

async def evaluate_with_gemini(
    annotated_matches: List[Dict[str, Any]],
    persona_mode: str,
    target_url: Optional[str]
) -> Dict[str, Any]:
    """Evaluates risk signals using Google Gemini structured JSON generation."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    user_prompt = f"""
Analyze the following reverse-image matches for a product image:
Persona Mode: {persona_mode.upper()}
Target URL (if submitted): {target_url or 'Direct image upload'}

Visual Matches from Reverse Image Search:
{json.dumps(annotated_matches, indent=2)}

Produce your structured JSON assessment following the system prompt and strict language rules.
"""
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    }
    async with _gemini_semaphore:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            res_data = resp.json()
            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_text)
            validated = GeminiVerdictSchema(**parsed)
            return validated.model_dump()

SYSTEM_PROMPT = """
You are Verix, an evidence summarizer for public reverse-image search results.
Your role is to analyze reverse-image search matches (Google Lens) for a given product photo and evaluate risk signals for a shopper (buyer mode) or an independent creator/seller (seller mode).

STRICT LANGUAGE POLICY:
1. You are strictly FORBIDDEN from using accusatory words: "scam", "scams", "scammer", "fraud", "fraudulent", "illegal", "criminal", "cheat", "fake", "stolen".
2. You MUST use objective, neutral risk terms instead, such as:
   - "unverified merchant domain"
   - "unverified price comparison"
   - "high-risk indicator"
   - "image appears on multiple sites"
   - "unverified seller"
   - "unconfirmed merchant registry"
3. You provide risk signals and evidence for users to evaluate; you do not pronounce guilt or legal verdicts.

EVALUATION METHODOLOGY:
- A recognized platform hostname is a source signal only. It does not verify its seller, product, or the submitted URL.
- Visual similarity does not establish an identical product, model, variant, condition, currency, or original source. Never infer a price disparity from these matches.
- Multiple image matches do not establish image ownership, permission, or unauthorized reuse.
- Whitelisted Platform Invariant: If the Target URL is on a recognized, whitelisted consumer marketplace (e.g. Amazon, Flipkart, Nike, Apple), the presence of the product image across other web listings and retail catalogs is normal catalog distribution across commercial distributors. For listings directly on these consumer-protected marketplaces, assign a high trust score (85-92) with 'low_risk' category, explaining that platform buyer protection applies while advising the shopper to check individual seller feedback.
- Persona context:
  - If persona is 'buyer': Recommend checking seller identity, terms and return policy directly; do not claim they were checked here.
  - If persona is 'seller': Suggest reviewing matches before considering any platform notice; do not assert infringement.

You MUST respond strictly with a valid JSON object matching this schema:
{
  "trust_score": <integer from 0 to 100>,
  "confidence": <"low" | "medium" | "high">,
  "explanation": "<2-4 sentences explaining the risk signals using neutral terminology>",
  "risk_category": <"trusted" | "low_risk" | "moderate_risk" | "high_risk">,
  "action_recommendation": "<Concise practical guidance for the user>",
  "flagged_domains": [
    {
      "domain": "<domain.com>",
      "flagged": <true|false>,
      "risk_note": "<Observed source signal only, never an allegation>"
    }
  ]
}
"""

async def evaluate_authenticity_with_groq(
    matches: List[Dict[str, Any]],
    persona_mode: str = "buyer",
    target_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends reverse-image match evidence to Groq LLaMA or Google Gemini for structured evaluation.
    Applies banned-word sanitization and deterministic platform-trust invariants to the output.
    """
    if not settings.ENABLE_LLM_EVALUATION:
        return evaluate_authenticity_heuristic(matches, persona_mode, target_url)

    # Pre-annotate matches with whitelist indicators
    annotated_matches = []
    for m in matches:
        is_wl, _ = is_domain_whitelisted(m.get("domain", ""))
        annotated_matches.append({
            "domain": m.get("domain"),
            "title": m.get("title"),
            "source": m.get("source"),
            "is_whitelisted": is_wl
        })

    data = None

    # Priority 1: Google Gemini (if valid key provided)
    if is_valid_api_key(settings.GEMINI_API_KEY):
        try:
            logger.info("Evaluating with Google Gemini structured reasoning engine...")
            data = await evaluate_with_gemini(annotated_matches, persona_mode, target_url)
        except Exception as gemini_err:
            logger.warning(f"Gemini evaluation failed, checking Groq/heuristic: {gemini_err}")

    # Priority 2: Groq LLaMA (if valid key provided and not already evaluated)
    if not data and is_valid_api_key(settings.GROQ_API_KEY):
        try:
            logger.info("Evaluating with Groq LLaMA structured reasoning engine...")
            client = AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=12.0)
            user_prompt = f"""
Analyze the following reverse-image matches for a product image:
Persona Mode: {persona_mode.upper()}
Target URL (if submitted): {target_url or 'Direct image upload'}

Visual Matches from Reverse Image Search:
{json.dumps(annotated_matches, indent=2)}

Produce your structured JSON assessment following the system prompt and strict language rules.
"""
            completion = await client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=800
            )
            raw_content = completion.choices[0].message.content
            data = json.loads(raw_content)
        except Exception as groq_err:
            logger.warning(f"Groq evaluation failed, falling back to heuristic: {groq_err}")

    # Priority 3: Built-in Deterministic Heuristic Engine (zero LLM / offline fallback)
    if not data:
        logger.info("Using deterministic heuristic evaluation engine.")
        return evaluate_authenticity_heuristic(matches, persona_mode, target_url)

    try:
        # Guardrail layer: Sanitize LLM explanation and notes against banned words
        explanation = sanitize_banned_words(data.get("explanation", ""))
        action_rec = sanitize_banned_words(data.get("action_recommendation", ""))
        trust_score = max(0, min(100, int(data.get("trust_score", 50))))
        confidence = data.get("confidence", "medium")
        if confidence not in ["low", "medium", "high"]:
            confidence = "medium"

        # Deterministic Invariant: Whitelisted platforms with buyer protection
        target_is_wl, target_wl_name = is_domain_whitelisted(target_url) if target_url else (False, None)
        if target_is_wl and trust_score < 85:
            trust_score = 88
            
        risk_category = data.get("risk_category", "moderate_risk")
        if target_is_wl:
            risk_category = "low_risk"
        elif risk_category not in ["trusted", "low_risk", "moderate_risk", "high_risk"]:
            if trust_score >= 80:
                risk_category = "low_risk"
            elif trust_score >= 50:
                risk_category = "moderate_risk"
            else:
                risk_category = "high_risk"

        flag_map = {item["domain"]: item for item in data.get("flagged_domains", []) if "domain" in item}
        
        # Merge flags into normalized match records
        enriched_matches = []
        for m in matches:
            domain = m.get("domain", "")
            is_wl, _ = is_domain_whitelisted(domain)
            flag_info = flag_map.get(domain, {})
            
            flagged = flag_info.get("flagged", False) and not is_wl
            risk_note = flag_info.get("risk_note") or m.get("risk_note")
            if risk_note:
                risk_note = sanitize_banned_words(risk_note)
                
            enriched_matches.append({
                **m,
                "flagged": flagged,
                "risk_note": risk_note,
                "is_whitelisted": is_wl
            })

        return {
            "trust_score": trust_score,
            "confidence": confidence,
            "explanation": explanation,
            "risk_category": risk_category,
            "action_recommendation": action_rec,
            "matched_domains": sanitize_matched_domains(enriched_matches)
        }

    except Exception as exc:
        logger.error(f"Error post-processing LLM evaluation: {str(exc)}. Falling back to deterministic analysis.")
        return evaluate_authenticity_heuristic(matches, persona_mode, target_url)


def evaluate_authenticity_heuristic(
    matches: List[Dict[str, Any]],
    persona_mode: str = "buyer",
    target_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Deterministic source-coverage heuristic. It is not a calibrated probability
    of seller legitimacy, item authenticity, or image ownership.
    """
    whitelisted_count = 0
    unverified_count = 0
    whitelisted_domains = []
    
    for m in matches:
        domain = m.get("domain", "")
        is_wl, wl_name = is_domain_whitelisted(domain)
        if is_wl:
            whitelisted_count += 1
            if wl_name:
                whitelisted_domains.append(wl_name)
        else:
            unverified_count += 1
            
    distinct_wl = sorted(list(set(whitelisted_domains)))
    target_is_wl, target_wl_name = is_domain_whitelisted(target_url) if target_url else (False, None)

    # Scoring formulation
    if target_is_wl:
        # User is shopping directly on a verified platform (e.g. Amazon, Flipkart, Nike)
        base_score = 85
        if len(matches) >= 5:
            base_score += 5  # Established catalog product
        final_score = min(95, base_score)
        confidence = "high"
        risk_category = "low_risk"
    else:
        base_score = 70
        if whitelisted_count > 0:
            base_score += min(20, whitelisted_count * 8)
        if unverified_count > 2:
            scale = 6 if whitelisted_count > 0 else 12
            base_score -= min(35, (unverified_count - 1) * scale)
        
        final_score = max(5, min(95, base_score))
        confidence = "medium" if len({m.get("domain") for m in matches}) >= 2 else "low"
        if final_score >= 80:
            risk_category = "low_risk"
        elif final_score >= 50:
            risk_category = "moderate_risk"
        else:
            risk_category = "high_risk"

    enriched_matches = []
    for m in matches:
        domain = m.get("domain", "")
        is_wl, _ = is_domain_whitelisted(domain)
        is_flagged = False
        risk_note = None
        
        if is_wl:
            risk_note = "Recognized platform hostname; individual seller and item not verified."
        elif unverified_count >= 2:
            is_flagged = True
            risk_note = "Image match on a domain outside the recognized-platform list; authorization unknown."
            
        enriched_matches.append({
            **m,
            "flagged": is_flagged,
            "risk_note": risk_note,
            "is_whitelisted": is_wl
        })

    if persona_mode == "seller":
        if unverified_count > 0:
            wl_prefix = f"including recognized listings on {', '.join(distinct_wl[:2])} and " if distinct_wl else ""
            explanation = (
                f"We found {len(matches)} public image-match listings, {wl_prefix}"
                f"{unverified_count} domain(s) outside the recognized-platform list. "
                "Image matches alone cannot establish ownership or permission."
            )
            action_rec = (
                "Review each match and confirm your rights and the site's authorization before considering a platform notice."
            )
        else:
            explanation = (
                f"This search returned {whitelisted_count} image-match listing(s) on recognized platform domains. "
                "Search coverage is incomplete, and ownership or permission was not checked."
            )
            action_rec = "Review the linked sources if you need to investigate use of your image."
    else:
        if risk_category == "high_risk":
            explanation = (
                f"This product photo appears on {len(matches)} web sources with notable risk indicators: "
                f"{unverified_count} domain(s) outside the recognized-platform list. "
                "This does not establish product identity, seller legitimacy, or image origin."
            )
            action_rec = (
                "Check the specific seller, return terms, and payment protections before purchasing."
            )
        elif risk_category == "moderate_risk":
            if target_url and is_domain_whitelisted(target_url)[0]:
                target_dom = is_domain_whitelisted(target_url)[1] or "recognized marketplace"
                explanation = (
                    f"The submitted link is on a recognized platform ({target_dom}). "
                    f"However, this photo was also found across {unverified_count} other web sources. "
                    "Since catalog photography is frequently reused by multiple third-party sellers, "
                    "verify the specific seller's store ratings and return policy."
                )
            elif distinct_wl:
                wl_str = ", ".join(distinct_wl[:2])
                explanation = (
                    f"The image matches recognized catalog listings on {wl_str}, but also appears across "
                    f"{unverified_count} domain(s) outside the recognized-platform list. Because commercial "
                    "catalog photos are easily copied across the web, check the specific seller's feedback and return terms."
                )
            else:
                explanation = (
                    f"The image appears in {len(matches)} public search result(s). Some listing hosts "
                    "are outside the recognized-platform list; their sellers were not verified."
                )
            action_rec = (
                "Moderate caution advised. Confirm return policies and verify whether the merchant provides "
                "standard buyer dispute protection before entering payment details."
            )
        else:
            if target_is_wl:
                target_dom = target_wl_name or "recognized marketplace"
                is_direct_brand_store = any(dom in target_dom.lower() for dom in [
                    "boat-lifestyle.com", "apple.com", "nike.com", "adidas", "samsung.com",
                    "sony.com", "sony.co.in", "zara.com", "hm.com", "uniqlo.com", "puma.com"
                ])
                if is_direct_brand_store:
                    explanation = (
                        f"The submitted listing is hosted on the official direct brand flagship store ({target_dom}). "
                        f"Corroborating public catalog references were identified across {len(matches)} listings. "
                        "As the authorized manufacturer and primary rights-holder, direct purchases carry official warranty and authenticity guarantees."
                    )
                    action_rec = f"Official brand flagship ({target_dom}). Direct manufacturer purchase with standard brand warranty."
                else:
                    explanation = (
                        f"The submitted listing is on a recognized, consumer-protected marketplace ({target_dom}). "
                        f"Corroborating public catalog references were identified across {len(matches)} listings. "
                        "Commercial catalog photography is standard across authorized retail distributors; "
                        "verify the specific seller's store rating and return policy before completing your purchase."
                    )
                    action_rec = "Platform buyer protection applies. Review the seller rating and return window before purchasing."
            elif distinct_wl:
                wl_str = ", ".join(distinct_wl[:3])
                explanation = (
                    f"The search confirmed image matches on recognized platform listings ({wl_str}). "
                    "While the platform is verified, Verix recommends confirming the specific third-party seller and return policy."
                )
                action_rec = "Confirm the exact product variant, seller and return policy before purchasing."
            else:
                explanation = (
                    f"The search returned image matches on {whitelisted_count} recognized platform listing(s). "
                    "Verix did not establish an exact product match or verify any seller."
                )
                action_rec = "Confirm the exact product variant, seller and return policy before purchasing."


    # Final post-processing pass through banned word sanitizer
    explanation = sanitize_banned_words(explanation)
    action_rec = sanitize_banned_words(action_rec)

    return {
        "trust_score": final_score,
        "confidence": confidence,
        "explanation": explanation,
        "risk_category": risk_category,
        "action_recommendation": action_rec,
        "matched_domains": sanitize_matched_domains(enriched_matches)
    }
