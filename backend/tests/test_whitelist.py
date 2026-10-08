"""Unit tests for trusted-platform source signals and multi-source analysis."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db
from backend.app.services.whitelist import is_domain_whitelisted, extract_domain
from backend.app.api.v1.analyze import _annotate_source_legitimacy


def create_sample_image_bytes() -> bytes:
    image = Image.new("RGB", (32, 32), color=(73, 109, 137))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_source_identity_comes_from_listing_url():
    match = _annotate_source_legitimacy({
        "domain": "amazon.in",
        "is_whitelisted": True,
        "link": "https://unrecognized.example/item",
    })
    assert match["domain"] == "unrecognized.example"
    assert match["is_whitelisted"] is False
    assert match["legitimacy_score"] is None

@pytest.mark.asyncio
async def test_domain_extraction():
    assert extract_domain("https://www.amazon.in/dp/B08N5WRWNW") == "amazon.in"
    assert extract_domain("https://m.flipkart.com/item/123") == "m.flipkart.com"
    assert extract_domain("http://nike.com/shoes") == "nike.com"
    assert extract_domain("nykaa.com") == "nykaa.com"

@pytest.mark.asyncio
async def test_whitelist_matching():
    # True positives for major Indian & Global marketplaces
    assert is_domain_whitelisted("https://www.amazon.in/product/123")[0] is True
    assert is_domain_whitelisted("https://m.flipkart.com/view")[0] is True
    assert is_domain_whitelisted("https://meesho.com/saree")[0] is True
    assert is_domain_whitelisted("https://myntra.com/tshirt")[0] is True
    assert is_domain_whitelisted("https://www.apple.com/iphone")[0] is True
    assert is_domain_whitelisted("https://www.nike.com/in/t/shoes")[0] is True
    
    # False positives (unverified/scammy domains)
    assert is_domain_whitelisted("https://sneakerdeals-scam.xyz/item")[0] is False
    assert is_domain_whitelisted("https://amazon-discount-store.cc")[0] is False
    assert is_domain_whitelisted("https://fake-flipkart-store.net")[0] is False

@pytest.mark.asyncio
async def test_whitelist_bypass_endpoint_execution():
    """Verify trusted platforms remain source evidence while the full pipeline runs."""
    await init_db()

    submitted_url = "https://www.flipkart.com/sony-wh-1000xm5/p/itm12345"
    matches = [
        {
            "domain": "flipkart.com",
            "title": "Sony WH-1000XM5 headphones",
            "price": "₹24,999",
            "extracted_price": 24999,
            "currency": "INR",
            "link": f"{submitted_url}?utm_source=serpapi",
            "source": "Flipkart",
            "thumbnail": "https://images.example.com/sony.jpg",
            "flagged": False,
            "engine": "submitted_listing",
            "evidence_type": "source_reference",
        },
        {
            "domain": "sony.co.in",
            "title": "Sony WH-1000XM5 official product page",
            "price": "₹29,990",
            "extracted_price": 29990,
            "currency": "INR",
            "link": "https://www.sony.co.in/electronics/headband-headphones/wh-1000xm5",
            "source": "Sony",
            "thumbnail": "https://images.example.com/sony-official.jpg",
            "flagged": False,
            "engine": "google_lens",
            "evidence_type": "visual_match",
        },
    ]
    extraction = (create_sample_image_bytes(), "https://cdn.example.com/sony.jpg", "Sony WH-1000XM5", "in_stock")
    verdict = {
        "trust_score": 88,
        "confidence": "high",
        "explanation": "The submitted listing is on Flipkart, while the official Sony reference provides a second corroborating source. Review the individual seller before buying.",
        "risk_category": "low_risk",
        "action_recommendation": "Confirm the seller rating and return policy before purchase.",
        "matched_domains": matches,
    }

    transport = ASGITransport(app=app)
    with (
        patch("backend.app.api.v1.analyze.extract_product_image_from_url", new=AsyncMock(return_value=extraction)),
        patch("backend.app.api.v1.analyze.search_google_lens", new=AsyncMock(return_value=list(matches))),
        patch("backend.app.api.v1.analyze.enrich_with_secondary_engines", new=AsyncMock(return_value=list(matches))),
        patch("backend.app.api.v1.analyze.evaluate_authenticity_with_groq", new=AsyncMock(return_value=verdict)),
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/analyze",
                data={"url": submitted_url, "persona_mode": "buyer"},
            )
            history_response = await ac.get(f"/api/v1/scans/{response.json()['id']}")
            signed_url = response.json()["image_url"]
            image_response = await ac.get(signed_url)
            unsigned_response = await ac.get(signed_url.split("?")[0])
            tampered_response = await ac.get(f"{signed_url}x")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert data["is_whitelist_bypass"] is False
    assert data["trust_score"] == 88
    assert data["confidence"] == "high"
    assert data["risk_category"] == "low_risk"
    assert data["provenance"] == "live_serpapi"
    assert data["product_availability"] == "in_stock"
    assert len(data["matched_domains"]) == 2

    flipkart = next(item for item in data["matched_domains"] if item["domain"] == "flipkart.com")
    assert flipkart["is_whitelisted"] is True
    assert flipkart["legitimacy_label"] == "Recognized platform domain"
    assert flipkart["legitimacy_score"] is None
    assert any("Seller and item authenticity" in reason for reason in flipkart["legitimacy_reasons"])
    assert flipkart["observed_at"]

    assert history_response.status_code == 200
    assert history_response.json()["product_availability"] == "in_stock"
    assert signed_url.startswith("/uploads/")
    assert image_response.status_code == 200
    assert unsigned_response.status_code in {404, 422}
    assert tampered_response.status_code == 404
