"""Tests for bounded, deduplicated secondary SerpApi evidence."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.app.config import settings
from backend.app.services.serpapi import canonicalize_evidence_url, enrich_with_secondary_engines


def test_evidence_url_canonicalization_removes_tracking_variants():
    first = "https://Store.Example/product/123/?utm_source=google&color=black#reviews"
    second = "https://store.example/product/123?color=black&utm_campaign=spring"

    assert canonicalize_evidence_url(first) == "https://store.example/product/123?color=black"
    assert canonicalize_evidence_url(first) == canonicalize_evidence_url(second)


def test_multi_engine_is_enabled_by_default():
    assert settings.ENABLE_MULTI_ENGINE is True


@pytest.mark.asyncio
async def test_secondary_engines_are_bounded_and_deduplicated():
    base = [{"domain": "nike.com", "title": "Air Jordan 1 Retro", "link": "https://nike.com/a", "engine": "google_lens"}]
    shopping = [{"domain": "store.example", "title": "Air Jordan 1 Retro", "link": "https://store.example/a?utm_source=shopping", "engine": "google_shopping"}]
    web = [{"domain": "store.example", "title": "Air Jordan 1 Retro", "link": "https://store.example/a#reviews", "engine": "google"}]

    with patch.object(settings, "ENABLE_MULTI_ENGINE", True), patch.object(settings, "SERPAPI_MAX_SECONDARY_CALLS", 2), \
         patch("backend.app.services.serpapi.search_google_shopping", new=AsyncMock(return_value=shopping)) as shopping_call, \
         patch("backend.app.services.serpapi.search_google_web", new=AsyncMock(return_value=web)) as web_call:
        result = await enrich_with_secondary_engines(base)

    assert len(result) == 2
    corroborated = next(item for item in result if item["domain"] == "store.example")
    assert corroborated["corroboration_count"] == 2
    assert corroborated["engines"] == ["google", "google_shopping"]
    assert corroborated["evidence_types"] == []
    assert shopping_call.await_count == 1
    assert web_call.await_count == 1
