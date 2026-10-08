"""Unit and integration tests for the Insufficient Data guardrail (< 2 matches)."""

import pytest
import io
from PIL import Image
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db
from backend.app.api.v1.analyze import _has_sufficient_evidence
from backend.app.services.availability import append_availability_guidance
from backend.app.services.groq_agent import evaluate_authenticity_heuristic, evaluate_authenticity_with_groq
from backend.app.services.serpapi import search_google_lens, SerpApiDegradedException
from unittest.mock import patch

def create_sample_image_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_evidence_requires_distinct_source_domains():
    same_domain = [
        {"domain": "shop.example", "link": "https://shop.example/a"},
        {"domain": "www.shop.example", "link": "https://shop.example/b"},
    ]
    distinct_domains = [
        {"domain": "shop.example", "link": "https://shop.example/a"},
        {"domain": "brand.example", "link": "https://brand.example/a"},
    ]

    assert _has_sufficient_evidence(same_domain) is False
    assert _has_sufficient_evidence(distinct_domains) is True


def test_availability_guidance_does_not_claim_authenticity_failure():
    guidance = append_availability_guidance("Review the seller before purchasing.", "discontinued")

    assert "discontinued" in guidance
    assert "does not prove inauthenticity" in guidance


def test_unmatched_prices_do_not_change_score_or_claim_a_benchmark():
    listings = [
        {"domain": "amazon.in", "link": "https://amazon.in/a", "extracted_price": 100000, "currency": "INR"},
        {"domain": "example.com", "link": "https://example.com/b", "extracted_price": 100, "currency": "USD"},
    ]
    with_prices = evaluate_authenticity_heuristic(listings)
    without_prices = evaluate_authenticity_heuristic([
        {**item, "extracted_price": None} for item in listings
    ])
    assert with_prices["trust_score"] == without_prices["trust_score"]
    assert with_prices["risk_category"] == without_prices["risk_category"]
    assert "price" not in with_prices["explanation"].lower()
    assert "verified seller" not in with_prices["explanation"].lower()
    assert "authorized" not in with_prices["explanation"].lower()


@pytest.mark.asyncio
async def test_public_default_does_not_call_a_generating_model():
    listings = [
        {"domain": "amazon.in", "link": "https://amazon.in/a"},
        {"domain": "example.com", "link": "https://example.com/b"},
    ]
    with patch("backend.app.services.groq_agent.settings.ENABLE_LLM_EVALUATION", False), patch(
        "backend.app.services.groq_agent.evaluate_with_gemini"
    ) as model:
        result = await evaluate_authenticity_with_groq(listings)
    model.assert_not_called()
    assert result["trust_score"] == evaluate_authenticity_heuristic(listings)["trust_score"]


@pytest.mark.asyncio
async def test_real_input_cannot_fall_back_to_mock_search():
    with patch("backend.app.services.serpapi.settings.SERPAPI_API_KEY", None), patch(
        "backend.app.services.serpapi.settings.ENABLE_MOCK_FALLBACK", True
    ):
        with pytest.raises(SerpApiDegradedException):
            await search_google_lens("https://example.com/product.jpg")

@pytest.mark.asyncio
async def test_insufficient_data_guardrail():
    """
    Asserts that when fewer than 2 matches are returned, the system:
    1. Returns status 'insufficient_data'
    2. Sets trust_score to None (null) - NO fake scores
    3. Sets confidence to 'low'
    4. Categorizes as 'insufficient_data'
    """
    await init_db()
    
    img_bytes = create_sample_image_bytes()
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"file": ("test_rare_item.jpg", img_bytes, "image/jpeg")}
        data = {
            "persona_mode": "buyer",
            "scenario": "insufficient"  # Triggers mock with 1 match
        }
        
        response = await ac.post("/api/v1/analyze", data=data, files=files)
        assert response.status_code == 200
        result = response.json()
        
        # Core Invariants
        assert result["status"] == "insufficient_data"
        assert result["trust_score"] is None, "trust_score MUST be null when insufficient data is returned!"
        assert result["confidence"] == "low"
        assert result["risk_category"] == "insufficient_data"
        assert "insufficient" in result["explanation"].lower() or "fewer than 2" in result["explanation"].lower()
        assert len(result["matched_domains"]) < 2
