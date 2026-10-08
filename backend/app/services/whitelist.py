"""Recognized platform domain matcher."""

from urllib.parse import urlparse
from typing import Optional, Tuple
from backend.app.config import settings

def extract_domain(url_or_domain: str) -> str:
    """Extracts and normalizes the apex/host domain from a URL or raw domain string."""
    cleaned = url_or_domain.strip().lower()
    if not cleaned.startswith(("http://", "https://")):
        cleaned = "https://" + cleaned
    
    try:
        parsed = urlparse(cleaned)
        netloc = parsed.netloc or parsed.path.split("/")[0]
        # Remove port if present
        domain = netloc.split(":")[0]
        # Strip leading www.
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""

def is_domain_whitelisted(url_or_domain: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if the given URL or domain matches any whitelisted trusted platform.
    Returns (is_whitelisted, matched_whitelisted_domain).
    """
    domain = extract_domain(url_or_domain)
    if not domain:
        return False, None

    for trusted in settings.WHITELISTED_DOMAINS:
        trusted_lower = trusted.lower()
        if domain == trusted_lower or domain.endswith("." + trusted_lower):
            return True, trusted_lower

    return False, None
