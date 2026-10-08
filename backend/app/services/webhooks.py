"""Enterprise Marketplace Webhook & Real-Time Fraud Event Dispatcher.

Dispatches cryptographic HMAC-SHA256 signed event payloads to enterprise merchants,
brand owners, and marketplace abuse desks upon detection of high-risk listings,
counterfeit pricing collapse, or synthetic AI generated images.
"""

from typing import Dict, Any, List, Optional
import time
import uuid
import hmac
import hashlib
import json
import logging
import httpx
from datetime import datetime, timezone
from pydantic import BaseModel, Field

logger = logging.getLogger("verix.webhooks")

# Default in-memory / persistent registry for the server session
_SUBSCRIPTIONS: Dict[str, Dict[str, Any]] = {}
_EVENT_HISTORY: List[Dict[str, Any]] = []

MAX_EVENT_HISTORY = 50

class WebhookSubscription(BaseModel):
    id: str
    url: str
    secret: str
    event_types: List[str]
    is_active: bool = True
    created_at: str
    last_delivery_at: Optional[str] = None
    last_status_code: Optional[int] = None


def generate_webhook_secret() -> str:
    """Generates a secure 32-byte hex secret for HMAC signing."""
    import secrets
    return secrets.token_hex(32)


def compute_signature(secret: str, timestamp: int, body_bytes: bytes) -> str:
    """
    Computes Stripe-style HMAC-SHA256 signature:
    signature = HMAC_SHA256(secret, f"{timestamp}.{body}")
    Returns header value: t={timestamp},v1={hex_digest}
    """
    to_sign = f"{timestamp}.".encode("utf-8") + body_bytes
    digest = hmac.new(secret.encode("utf-8"), to_sign, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def verify_signature(secret: str, signature_header: str, body_bytes: bytes, tolerance_seconds: int = 300) -> bool:
    """Verifies HMAC signature and protects against replay attacks."""
    try:
        parts = dict(item.split("=", 1) for item in signature_header.split(","))
        ts = int(parts.get("t", 0))
        provided_sig = parts.get("v1", "")

        now = int(time.time())
        if abs(now - ts) > tolerance_seconds:
            return False

        to_sign = f"{ts}.".encode("utf-8") + body_bytes
        expected = hmac.new(secret.encode("utf-8"), to_sign, hashlib.sha256).hexdigest()
        return hmac.compare_digest(provided_sig, expected)
    except Exception:
        return False


def register_subscription(
    url: str,
    event_types: Optional[List[str]] = None,
    secret: Optional[str] = None
) -> Dict[str, Any]:
    """Registers a new webhook subscription."""
    sub_id = str(uuid.uuid4())
    sec = secret or generate_webhook_secret()
    events = event_types or ["verix.event.all"]
    now_iso = datetime.now(timezone.utc).isoformat()

    sub = {
        "id": sub_id,
        "url": url,
        "secret": sec,
        "event_types": events,
        "is_active": True,
        "created_at": now_iso,
        "last_delivery_at": None,
        "last_status_code": None
    }
    _SUBSCRIPTIONS[sub_id] = sub
    return sub


def list_subscriptions() -> List[Dict[str, Any]]:
    """Lists registered subscriptions with masked secrets."""
    out = []
    for s in _SUBSCRIPTIONS.values():
        masked_sec = f"{s['secret'][:6]}...{s['secret'][-4:]}" if len(s['secret']) > 12 else "******"
        copy_s = dict(s)
        copy_s["secret_masked"] = masked_sec
        out.append(copy_s)
    return out


def remove_subscription(sub_id: str) -> bool:
    """Removes a subscription by ID."""
    if sub_id in _SUBSCRIPTIONS:
        del _SUBSCRIPTIONS[sub_id]
        return True
    return False


async def dispatch_webhook_event(event_type: str, payload_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Asynchronously delivers a signed webhook event to all subscribed endpoints.
    """
    event_id = str(uuid.uuid4())
    ts = int(time.time())
    now_iso = datetime.now(timezone.utc).isoformat()

    full_payload = {
        "event_id": event_id,
        "event_type": event_type,
        "timestamp": ts,
        "created_at": now_iso,
        "data": payload_data
    }
    body_bytes = json.dumps(full_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    # Record in history
    _EVENT_HISTORY.insert(0, {
        "event_id": event_id,
        "event_type": event_type,
        "timestamp": now_iso,
        "summary": str(payload_data.get("summary") or event_type)
    })
    if len(_EVENT_HISTORY) > MAX_EVENT_HISTORY:
        _EVENT_HISTORY.pop()

    dispatched = []

    for sub_id, sub in list(_SUBSCRIPTIONS.items()):
        if not sub.get("is_active"):
            continue

        subscribed_events = sub.get("event_types", [])
        if "verix.event.all" not in subscribed_events and event_type not in subscribed_events:
            continue

        sig_header = compute_signature(sub["secret"], ts, body_bytes)
        headers = {
            "Content-Type": "application/json",
            "X-Verix-Event": event_type,
            "X-Verix-Id": event_id,
            "X-Verix-Signature": sig_header,
            "User-Agent": "Verix-Webhook-Dispatcher/1.0"
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(sub["url"], content=body_bytes, headers=headers)
                sub["last_delivery_at"] = now_iso
                sub["last_status_code"] = res.status_code
                dispatched.append({"sub_id": sub_id, "url": sub["url"], "status": res.status_code, "success": res.is_success})
        except Exception as exc:
            logger.debug("Webhook delivery to %s failed: %s", sub["url"], exc)
            sub["last_delivery_at"] = now_iso
            sub["last_status_code"] = 0
            dispatched.append({"sub_id": sub_id, "url": sub["url"], "status": 0, "success": False, "error": str(exc)})

    return dispatched


async def send_test_ping(target_url: str, secret: Optional[str] = None) -> Dict[str, Any]:
    """Sends a single synchronous test event to a target URL."""
    sec = secret or "verix-test-secret-2026"
    event_id = str(uuid.uuid4())
    ts = int(time.time())
    now_iso = datetime.now(timezone.utc).isoformat()

    payload = {
        "event_id": event_id,
        "event_type": "verix.event.ping",
        "timestamp": ts,
        "created_at": now_iso,
        "data": {
            "message": "Verix webhook delivery test ping",
            "test_mode": True,
            "system": "Verix Authenticity Intelligence"
        }
    }
    body_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig_header = compute_signature(sec, ts, body_bytes)

    headers = {
        "Content-Type": "application/json",
        "X-Verix-Event": "verix.event.ping",
        "X-Verix-Id": event_id,
        "X-Verix-Signature": sig_header,
        "User-Agent": "Verix-Webhook-Dispatcher/1.0"
    }

    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(target_url, content=body_bytes, headers=headers)
            dt_ms = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "success": res.is_success,
                "status_code": res.status_code,
                "latency_ms": dt_ms,
                "signature_header": sig_header,
                "event_id": event_id
            }
    except Exception as exc:
        dt_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "success": False,
            "status_code": 0,
            "latency_ms": dt_ms,
            "error": str(exc),
            "signature_header": sig_header,
            "event_id": event_id
        }


def get_recent_events() -> List[Dict[str, Any]]:
    """Returns recent dispatched event log."""
    return list(_EVENT_HISTORY)
