"""Tests for Enterprise Webhook Dispatcher and Signature Engine."""

import pytest
import time
import json
import httpx
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from backend.app.main import app
from backend.app.services.webhooks import (
    register_subscription,
    list_subscriptions,
    remove_subscription,
    compute_signature,
    verify_signature,
    send_test_ping,
    get_recent_events,
    _SUBSCRIPTIONS,
    _EVENT_HISTORY
)

@pytest.fixture(autouse=True)
def clean_subscriptions():
    _SUBSCRIPTIONS.clear()
    _EVENT_HISTORY.clear()
    yield
    _SUBSCRIPTIONS.clear()
    _EVENT_HISTORY.clear()

def test_signature_generation_and_verification():
    secret = "test_super_secret_key_123"
    payload = {"event": "high_risk_detected", "scan_id": "test-123", "trust_score": 15.0}
    body_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    timestamp = int(time.time())

    header = compute_signature(secret, timestamp, body_bytes)
    assert header.startswith(f"t={timestamp},v1=")

    # Verify signature passes
    valid = verify_signature(secret, header, body_bytes, tolerance_seconds=300)
    assert valid is True

def test_signature_verification_tamper_rejection():
    secret = "test_super_secret_key_123"
    payload = {"event": "high_risk_detected", "scan_id": "test-123"}
    body_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    timestamp = int(time.time())

    header = compute_signature(secret, timestamp, body_bytes)

    # Tamper with payload
    tampered_bytes = json.dumps({"event": "high_risk_detected", "scan_id": "test-tampered"}).encode("utf-8")
    valid = verify_signature(secret, header, tampered_bytes, tolerance_seconds=300)
    assert valid is False

def test_signature_verification_replay_attack_rejection():
    secret = "test_super_secret_key_123"
    body_bytes = b'{"event":"high_risk_detected"}'
    old_timestamp = int(time.time()) - 400  # 400 seconds in past

    header = compute_signature(secret, old_timestamp, body_bytes)
    valid = verify_signature(secret, header, body_bytes, tolerance_seconds=300)
    assert valid is False

@pytest.mark.asyncio
async def test_subscription_lifecycle_and_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register a webhook
        create_resp = await ac.post("/api/v1/webhooks", json={
            "url": "https://example.com/webhook",
            "event_types": ["high_risk", "pricing_anomaly"],
            "secret": "my_secret_key_123456"
        })
        assert create_resp.status_code == 201
        sub_data = create_resp.json()
        assert sub_data["url"] == "https://example.com/webhook"
        sub_id = sub_data["id"]

        # List webhooks
        list_resp = await ac.get("/api/v1/webhooks")
        assert list_resp.status_code == 200
        subs = list_resp.json()["subscriptions"]
        assert len(subs) == 1
        assert subs[0]["id"] == sub_id
        assert "secret_masked" in subs[0]

        # Delete webhook
        del_resp = await ac.delete(f"/api/v1/webhooks/{sub_id}")
        assert del_resp.status_code == 200

        # Confirm list is empty
        list_resp2 = await ac.get("/api/v1/webhooks")
        assert len(list_resp2.json()["subscriptions"]) == 0

@pytest.mark.asyncio
async def test_webhook_test_ping_direct():
    mock_response = httpx.Response(200, json={"received": True})
    with patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock, return_value=mock_response):
        res = await send_test_ping("https://test-receiver.org/events", "simulated_secret_token")
        assert res["success"] is True
        assert res["status_code"] == 200
        assert "signature_header" in res
        assert "t=" in res["signature_header"]

@pytest.mark.asyncio
async def test_webhook_test_ping_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("backend.app.api.v1.webhooks.send_test_ping", new_callable=AsyncMock) as mock_ping:
            mock_ping.return_value = {
                "success": True,
                "status_code": 200,
                "latency_ms": 12.5,
                "signature_header": "t=12345,v1=abc",
                "event_id": "evt-123"
            }
            resp = await ac.post("/api/v1/webhooks/test", json={
                "url": "https://test-receiver.org/events",
                "secret": "simulated_secret_token"
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["status_code"] == 200
            assert data["signature_header"] == "t=12345,v1=abc"


@pytest.mark.asyncio
async def test_webhook_verify_endpoint():
    secret = "shared_webhook_secret_key"
    payload = {"scan_id": "test-uuid", "event": "pricing_anomaly"}
    raw_body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    timestamp = int(time.time())
    sig_header = compute_signature(secret, timestamp, raw_body.encode("utf-8"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/webhooks/verify", json={
            "raw_body": raw_body,
            "signature_header": sig_header,
            "secret": secret
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
