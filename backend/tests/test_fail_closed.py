"""Tests for Fail-Closed circuit breaker and stale cache retrieval on SerpApi downtime/timeout."""

import pytest
import io
import uuid
from datetime import datetime, timezone
from unittest.mock import patch
from PIL import Image
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db, AsyncSessionLocal
from backend.app.models.scan import ScanRecord
from backend.app.services.storage import compute_image_hashes
from backend.app.services.serpapi import SerpApiDegradedException

def create_sample_image_bytes(color=(120, 50, 90)) -> bytes:
    img = Image.new("RGB", (80, 80), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

@pytest.mark.asyncio
async def test_fail_closed_stale_cache_fallback():
    """
    Asserts that if SerpApi experiences a timeout or rate limit,
    the system retrieves the most recent scan by image hash and serves it with stale=True.
    """
    await init_db()
    
    img_bytes = create_sample_image_bytes()
    sha256_hash, _ = compute_image_hashes(img_bytes)
    original_time = datetime.now(timezone.utc)
    
    # 1. Pre-seed a historical scan record in the database
    async with AsyncSessionLocal() as session:
        seeded_scan = ScanRecord(
            id=str(uuid.uuid4()),
            image_hash=sha256_hash,
            created_at=original_time,
            persona_mode="buyer",
            input_type="upload",
            image_url="/uploads/historical.jpg",
            status="completed",
            trust_score=78,
            confidence="medium",
            explanation="Initial scan completed before upstream outage.",
            matched_domains=[
                {
                    "domain": "verified-partner.com",
                    "title": "Partner Listing",
                    "price": "₹1,200",
                    "extracted_price": 1200.0,
                    "currency": "INR",
                    "link": "https://verified-partner.com/item",
                    "source": "Partner Store",
                    "thumbnail": None,
                    "flagged": False,
                    "risk_note": None,
                    "is_whitelisted": False
                }
            ],
            is_whitelist_bypass=False,
            is_stale=False
        )
        session.add(seeded_scan)
        await session.commit()

    # 2. Simulate SerpApi failure using mock patch
    transport = ASGITransport(app=app)
    with patch("backend.app.api.v1.analyze.search_google_lens", side_effect=SerpApiDegradedException("Simulated 429 Rate Limit")):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"file": ("re_uploaded_item.jpg", img_bytes, "image/jpeg")}
            data = {"persona_mode": "buyer"}
            
            response = await ac.post("/api/v1/analyze", data=data, files=files)
            assert response.status_code == 200
            result = response.json()
            
            # 3. Assert fail-closed invariants
            assert result["is_stale"] is True
            assert result["status"] == "stale_cached"
            assert result["trust_score"] == 78
            assert result["stale_original_timestamp"] is not None
            assert "[Cached Verification]" in result["explanation"]
