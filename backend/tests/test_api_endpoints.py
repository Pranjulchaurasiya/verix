"""Integration tests for decoupled admin endpoints and history."""

import pytest
import uuid
import hashlib
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db, AsyncSessionLocal
from backend.app.models.scan import ScanRecord

@pytest.mark.asyncio
async def test_admin_health_decoupled():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/admin/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "uptime_seconds" in data
        assert data["database_connected"] is True
        assert "version" in data

@pytest.mark.asyncio
async def test_admin_stats():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/admin/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_scans" in data
        assert "whitelist_bypasses" in data
        assert "serpapi_success_rate" in data
        assert "persona_breakdown" in data

@pytest.mark.asyncio
async def test_scans_history_and_lookup():
    await init_db()
    scan_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        session.add(ScanRecord(
            id=scan_id,
            image_hash="a" * 64,
            created_at=datetime.now(timezone.utc),
            persona_mode="seller",
            input_type="url",
            source_url="https://example.com/product",
            image_url="https://example.com/product.jpg",
            client_scope_hash=hashlib.sha256(b"development-anonymous").hexdigest(),
            status="insufficient_data",
            trust_score=None,
            confidence="low",
            explanation="No independent source match.",
            matched_domains=[],
        ))
        await session.commit()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Fetch by ID
        get_resp = await ac.get(f"/api/v1/scans/{scan_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == scan_id
        assert get_resp.json()["persona_mode"] == "seller"

        # List scans
        list_resp = await ac.get("/api/v1/scans")
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        assert len(items) >= 1

        delete_resp = await ac.delete(f"/api/v1/scans/{scan_id}")
        assert delete_resp.status_code == 204
        assert (await ac.get(f"/api/v1/scans/{scan_id}")).status_code == 404
        assert (await ac.delete(f"/api/v1/scans/{scan_id}")).status_code == 404


@pytest.mark.asyncio
async def test_unextractable_marketplace_url_does_not_receive_a_score():
    await init_db()
    transport = ASGITransport(app=app)
    with patch("backend.app.api.v1.analyze.extract_product_image_from_url", new=AsyncMock(side_effect=ValueError("No product image"))), patch(
        "backend.app.api.v1.analyze.settings.ENABLE_MOCK_FALLBACK", True
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/api/v1/analyze", data={"url": "https://www.amazon.in/dp/missing"})
    assert response.status_code == 400
    assert "Could not extract" in response.json()["detail"]


@pytest.mark.asyncio
async def test_scan_export_json_and_csv():
    await init_db()
    scan_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        session.add(ScanRecord(
            id=scan_id,
            image_hash="b" * 64,
            created_at=datetime.now(timezone.utc),
            persona_mode="buyer",
            input_type="url",
            source_url="https://example.com/shoes",
            image_url="https://example.com/shoes.jpg",
            client_scope_hash=hashlib.sha256(b"development-anonymous").hexdigest(),
            status="completed",
            trust_score=85,
            confidence="high",
            explanation="Matches authenticated brand store.",
            matched_domains=[
                {
                    "domain": "nike.com",
                    "title": "Nike Air Max",
                    "price": "$150",
                    "extracted_price": 150.0,
                    "currency": "USD",
                    "legitimacy_label": "platform_registry",
                    "legitimacy_score": 95,
                    "engine": "google_lens",
                    "in_stock": True,
                    "flagged": False,
                    "risk_note": "Verified flagship.",
                    "link": "https://nike.com/shoes"
                }
            ],
        ))
        await session.commit()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        json_resp = await ac.get(f"/api/v1/scans/{scan_id}/export?format=json")
        assert json_resp.status_code == 200
        json_data = json_resp.json()
        assert json_data["scan_id"] == scan_id
        assert json_data["image_hash_sha256"] == "b" * 64
        assert "audit_verification" in json_data
        assert json_data["audit_verification"]["algorithm"] == "HMAC-SHA256"
        assert len(json_data["evidence_chain"]) == 1

        csv_resp = await ac.get(f"/api/v1/scans/{scan_id}/export?format=csv")
        assert csv_resp.status_code == 200
        assert "text/csv" in csv_resp.headers["content-type"]
        assert "Domain,Title,Price" in csv_resp.text
        assert "nike.com" in csv_resp.text


@pytest.mark.asyncio
async def test_batch_analysis_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "persona_mode": "buyer",
            "items": [
                {"url": "https://www.amazon.in/dp/B08L5WHJ2T", "label": "Amazon Verified Listing"},
                {"url": "https://www.flipkart.com/shoes/p/itm123", "label": "Flipkart Marketplace"},
            ]
        }
        resp = await ac.post("/api/v1/analyze/batch", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "batch_id" in data
        assert data["total_items"] == 2
        assert data["low_risk_count"] == 2
        assert "audit_signature" in data
        assert len(data["items"]) == 2
        assert data["items"][0]["status"] == "trusted_whitelist"
        assert data["items"][0]["trust_score"] == 95


