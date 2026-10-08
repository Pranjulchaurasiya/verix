"""Content sanitization and prompt injection defense services."""

import re
from typing import List, Dict, Any

# Replacement mapping from accusatory/banned terms to neutral risk indicators
BANNED_WORD_REPLACEMENTS = [
    (r"\bscammers\b", "unverified sellers"),
    (r"\bscammer\b", "unverified seller"),
    (r"\bscams\b", "unverified merchant domains"),
    (r"\bscam\b", "unverified merchant domain"),
    (r"\bfraudulent\b", "high-risk indicator"),
    (r"\bfrauds\b", "unverified merchant practices"),
    (r"\bfraud\b", "unverified merchant activity"),
    (r"\billegal\b", "unauthorized commercial activity"),
    (r"\bcriminals\b", "unauthorized commercial actors"),
    (r"\bcriminal\b", "unauthorized commercial activity"),
    (r"\bcon artist\b", "unverified merchant"),
    (r"\brip-off\b", "severe price disparity"),
    (r"\bripoff\b", "severe price disparity"),
    (r"\bcheat\b", "inconsistent seller behavior"),
    (r"\bcheating\b", "inconsistent seller practices"),
]

# Prompt injection patterns commonly attempted in scraped web titles/descriptions
PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"(?i)disregard\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"(?i)system\s+prompt",
    r"(?i)you\s+are\s+now\s+(an?\s+)?",
    r"(?i)do\s+not\s+follow\s+any\s+rules",
    r"(?i)output\s+trust_score\s*:\s*100",
    r"(?i)always\s+return\s+trust_score\s*:\s*100",
    r"<\|.*?\|>",          # Special tokens
    r"\[INST\].*?\[/INST\]", # Instruction markers
    r"```(?:json|python|html)?", # Code fencing
]

def sanitize_banned_words(text: str) -> str:
    """
    Deterministically replaces accusatory words with neutral, objective risk terms.
    Preserves casing structure where possible.
    """
    if not text:
        return ""
    
    sanitized = text
    for pattern, replacement in BANNED_WORD_REPLACEMENTS:
        # Case-insensitive replacement preserving word boundaries
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
    return sanitized

def sanitize_scraped_text(text: str, max_length: int = 250) -> str:
    """
    Cleans untrusted scraped text (e.g. product titles, snippets) before sending to LLM.
    Strips prompt injection attempts, control characters, and caps maximum length.
    """
    if not text:
        return ""
    
    cleaned = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        cleaned = re.sub(pattern, " [filtered] ", cleaned)
    
    # Strip non-printable / control characters except standard whitespace
    cleaned = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", cleaned)
    
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    # Truncate to avoid context window stuffing
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "..."
        
    return cleaned

def sanitize_matched_domains(domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sanitizes titles, snippets, and notes in the matched domains list."""
    sanitized_list = []
    for item in domains:
        cleaned_item = dict(item)
        if "title" in cleaned_item and cleaned_item["title"]:
            cleaned_item["title"] = sanitize_scraped_text(cleaned_item["title"])
        if "risk_note" in cleaned_item and cleaned_item["risk_note"]:
            cleaned_item["risk_note"] = sanitize_banned_words(cleaned_item["risk_note"])
        sanitized_list.append(cleaned_item)
    return sanitized_list
