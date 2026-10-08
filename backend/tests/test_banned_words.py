"""Tests for the Banned-Word Post-Processing Filter guardrail."""

import pytest
from backend.app.services.sanitizer import sanitize_banned_words
from backend.app.config import settings

def test_banned_word_filter_replaces_prohibited_terms():
    input_text = (
        "This website is a blatant scam and the merchant is a fraudulent scammer. "
        "They are running an illegal criminal fraud syndicate and cheating consumers."
    )
    
    sanitized = sanitize_banned_words(input_text)
    
    # Assert none of the strictly prohibited words appear in the output
    for banned in settings.BANNED_WORDS:
        assert banned not in sanitized.lower(), f"Prohibited word '{banned}' was found in sanitized output: '{sanitized}'"
        
    # Assert neutral terms replaced them
    assert "unverified merchant domain" in sanitized
    assert "high-risk indicator" in sanitized
    assert "unverified seller" in sanitized
    assert "unauthorized commercial activity" in sanitized

def test_banned_word_preserves_legitimate_content():
    clean_text = (
        "This product photo appears on 4 unverified merchant domains with extreme price disparity. "
        "Exercise caution before submitting payment information."
    )
    assert sanitize_banned_words(clean_text) == clean_text
