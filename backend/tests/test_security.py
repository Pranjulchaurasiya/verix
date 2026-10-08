"""Regression tests for upload, SSRF, and production admin protections."""

import io
from unittest.mock import patch

import pytest
from PIL import Image
from fastapi import HTTPException, Request
import httpx

from backend.app.services.scraper import _get_limited, _validate_public_url
from backend.app.services.storage import validate_image_bytes
from backend.app.api.v1.admin import require_admin_key
from backend.app.config import settings
from backend.app.services.rate_limiter import SlidingWindowRateLimiter, check_rate_limit


def test_rejects_private_and_non_http_urls():
    for url in ("http://127.0.0.1:8000/admin", "http://localhost/", "file:///etc/passwd"):
        with pytest.raises(ValueError):
            _validate_public_url(url)


@pytest.mark.asyncio
async def test_scraper_rejects_private_redirect_before_request():
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        return httpx.Response(302, headers={"location": "http://127.0.0.1/admin"})

    def resolve(hostname: str, _port: object) -> list[tuple]:
        address = "93.184.215.14" if hostname == "public.example" else hostname
        return [(None, None, None, None, (address, 0))]

    with patch("backend.app.services.scraper.socket.getaddrinfo", side_effect=resolve):
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(ValueError, match="Private or local"):
                await _get_limited(client, "https://public.example/product")

    assert requested == ["https://public.example/product"]


def test_accepts_valid_small_image():
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), color=(20, 30, 40)).save(buf, format="PNG")
    width, height, image_format = validate_image_bytes(buf.getvalue())
    assert (width, height, image_format) == (16, 16, "PNG")


def test_rejects_non_image_upload():
    with pytest.raises(ValueError, match="valid supported image"):
        validate_image_bytes(b"not an image")


def test_admin_key_required_outside_development():
    with patch.object(settings, "ENVIRONMENT", "production"), patch.object(settings, "ADMIN_API_KEY", "secret"):
        with pytest.raises(HTTPException) as exc:
            require_admin_key(None)
        assert exc.value.status_code == 401
        assert require_admin_key("secret") is None


def test_untrusted_forwarded_for_cannot_evade_rate_limit():
    limiter = SlidingWindowRateLimiter(limit_per_minute=1)
    def request(forwarded: str) -> Request:
        return Request({
            "type": "http",
            "client": ("203.0.113.10", 12345),
            "headers": [(b"x-forwarded-for", forwarded.encode())],
        })

    with patch("backend.app.services.rate_limiter.rate_limiter", limiter), patch.object(settings, "TRUSTED_PROXY_IPS", []):
        check_rate_limit(request("198.51.100.1"))
        with pytest.raises(HTTPException) as exc:
            check_rate_limit(request("198.51.100.2"))
    assert exc.value.status_code == 429
