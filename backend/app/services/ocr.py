"""Screenshot detection and visual OCR metadata extraction service."""

import re
from typing import Dict, Any, Optional, List
import logging
from PIL import Image
import io
import pytesseract
from backend.app.services.whitelist import is_domain_whitelisted

logger = logging.getLogger("verix.ocr")

# Common e-commerce & screenshot UI anchor terms
SCREENSHOT_UI_ANCHORS = [
    r"add to cart",
    r"buy now",
    r"in stock",
    r"free delivery",
    r"customer reviews",
    r"ratings?",
    r"sponsored",
    r"m\.r\.p",
    r"inclusive of all taxes",
    r"emi starts at",
    r"save \d+%",
    r"off",
    r"amazon\.in",
    r"flipkart",
    r"myntra",
    r"meesho",
    r"instagram",
]

# Regex patterns for domains
DOMAIN_PATTERN = re.compile(
    r"\b((?:[a-zA-Z0-9-]+\.)+(?:com|in|org|net|co\.in|club|shop|store|biz|online|io))\b",
    re.IGNORECASE
)

# Regex patterns for Indian Rupee & USD prices
PRICE_PATTERNS = [
    re.compile(r"[₹\u20B9]\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?)"),
    re.compile(r"(?:rs\.?|inr)\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?)", re.IGNORECASE),
    re.compile(r"\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)"),
]

def parse_price_str(price_raw: str) -> Optional[float]:
    try:
        clean = price_raw.replace(",", "").strip()
        val = float(clean)
        return val if val > 0 else None
    except Exception:
        return None

def detect_screenshot_and_extract_metadata(image_bytes: bytes) -> Dict[str, Any]:
    """
    Performs local visual OCR analysis on uploaded image to:
    1. Detect if image is an e-commerce / mobile app screenshot
    2. Extract originating platform domain (e.g. amazon.in, flipkart.com)
    3. Extract visible listing price
    4. Check if extracted domain matches our trusted Platform Whitelist
    """
    result: Dict[str, Any] = {
        "is_screenshot": False,
        "detected_domain": None,
        "detected_price": None,
        "is_whitelisted_source": False,
        "confidence": "none",
        "ocr_text_preview": None
    }
    
    if not image_bytes or len(image_bytes) < 100:
        return result

    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        
        # Aspect ratio heuristic: mobile screenshots often ~0.45 - 0.58, desktop ~1.6 - 1.8
        aspect_ratio = width / height if height > 0 else 1.0
        is_ratio_screenshot = (0.40 <= aspect_ratio <= 0.60) or (1.50 <= aspect_ratio <= 1.85)

        # Optimize for OCR: convert to grayscale if RGB
        gray_img = img.convert("L")
        
        # If very large, resize moderately to keep OCR fast (< 300ms)
        if max(width, height) > 1600:
            gray_img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            
        ocr_text = pytesseract.image_to_string(gray_img)
        if not ocr_text or len(ocr_text.strip()) == 0:
            return result
            
        clean_text = ocr_text.lower()
        result["ocr_text_preview"] = ocr_text[:200].strip()
        
        # 1. Match UI Anchors
        anchor_matches = 0
        for pattern in SCREENSHOT_UI_ANCHORS:
            if re.search(pattern, clean_text):
                anchor_matches += 1
                
        # 2. Extract Visible Domains
        detected_domain = None
        for match in DOMAIN_PATTERN.finditer(ocr_text):
            candidate = match.group(1).lower()
            if candidate.startswith("www."):
                candidate = candidate[4:]
            # Filter common false positives
            if candidate not in ["example.com", "schema.org", "w3.org"]:
                detected_domain = candidate
                break

        # Check domain whitelist
        is_wl = False
        if detected_domain:
            is_wl, _ = is_domain_whitelisted(detected_domain)
            
        # Specific check for ubiquitous Indian platforms if logo or text found
        if not detected_domain:
            if "amazon" in clean_text:
                detected_domain = "amazon.in"
                is_wl = True
            elif "flipkart" in clean_text:
                detected_domain = "flipkart.com"
                is_wl = True
            elif "myntra" in clean_text:
                detected_domain = "myntra.com"
                is_wl = True
            elif "meesho" in clean_text:
                detected_domain = "meesho.com"
                is_wl = True

        # 3. Extract Visible Listing Price
        detected_price = None
        for p_re in PRICE_PATTERNS:
            match = p_re.search(ocr_text)
            if match:
                price_val = parse_price_str(match.group(1))
                if price_val and price_val > 10:
                    detected_price = price_val
                    break

        # Decision on whether image is a screenshot
        is_screenshot = (anchor_matches >= 2) or (anchor_matches >= 1 and is_ratio_screenshot) or (detected_domain is not None and anchor_matches >= 1)
        
        result["is_screenshot"] = is_screenshot
        result["detected_domain"] = detected_domain
        result["detected_price"] = detected_price
        result["is_whitelisted_source"] = is_wl
        result["confidence"] = "high" if anchor_matches >= 2 else ("medium" if is_screenshot else "low")
        
        logger.info(
            f"OCR Analysis complete: is_screenshot={is_screenshot}, "
            f"domain={detected_domain} (whitelisted={is_wl}), "
            f"price={detected_price}, anchors={anchor_matches}"
        )
        return result

    except Exception as exc:
        logger.warning(f"Tesseract OCR analysis failed gracefully: {str(exc)}")
        return result
