"""Enterprise Marketplace Webhook Endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from backend.app.services.webhooks import (
    register_subscription,
    list_subscriptions,
    remove_subscription,
    send_test_ping,
    get_recent_events,
    verify_signature
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class SubscriptionCreateRequest(BaseModel):
    url: str = Field(..., description="Target HTTPS webhook URL to receive fraud events")
    event_types: Optional[List[str]] = Field(default=["verix.event.all"], description="Event topics to subscribe to")
    secret: Optional[str] = Field(None, description="Optional custom secret; if omitted, a secure 32-byte secret is generated")


class WebhookTestPingRequest(BaseModel):
    url: str = Field(..., description="Target webhook URL to test")
    secret: Optional[str] = Field(None, description="Secret to use for test HMAC signature")


class WebhookVerifyRequest(BaseModel):
    secret: str
    signature_header: str
    raw_body: str


@router.get("")
async def get_webhook_subscriptions():
    """Lists all configured webhook subscriptions with masked secrets."""
    return {"subscriptions": list_subscriptions()}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_webhook_subscription(payload: SubscriptionCreateRequest):
    """Registers a new webhook subscription for real-time risk events."""
    if not payload.url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook URL must begin with http:// or https://"
        )

    sub = register_subscription(
        url=payload.url,
        event_types=payload.event_types,
        secret=payload.secret
    )
    return sub


@router.delete("/{sub_id}")
async def delete_webhook_subscription(sub_id: str):
    """Removes an active webhook subscription."""
    success = remove_subscription(sub_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found."
        )
    return {"deleted": True, "id": sub_id}


@router.post("/test")
async def trigger_test_webhook_ping(payload: WebhookTestPingRequest):
    """Dispatches a test event to verify target endpoint connectivity and HMAC signature."""
    result = await send_test_ping(payload.url, payload.secret)
    return result


@router.get("/events")
async def get_dispatched_webhook_events():
    """Returns the most recent dispatched fraud and risk webhook events."""
    return {"events": get_recent_events()}


@router.post("/verify")
async def verify_webhook_signature_endpoint(payload: WebhookVerifyRequest):
    """Utility endpoint for developers to verify an incoming webhook payload and signature."""
    body_bytes = payload.raw_body.encode("utf-8")
    is_valid = verify_signature(payload.secret, payload.signature_header, body_bytes)
    return {
        "valid": is_valid,
        "message": "Signature verified successfully" if is_valid else "Signature mismatch or expired timestamp"
    }
