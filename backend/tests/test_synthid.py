"""Tests for Unified Google DeepMind SynthID & Synthetic Provenance Service."""

import pytest
import io
from PIL import Image, PngImagePlugin
from unittest.mock import AsyncMock, patch

from backend.app.services.synthid import SynthIDService, synthid_service

def test_synthid_tier1_clean_image():
    img = Image.new("RGB", (32, 32), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = SynthIDService.inspect_metadata_and_bytes(buf.getvalue())
    
    assert res["is_synthetic"] is False
    assert res["synthid_detected"] is False
    assert res["provenance_score"] == 0.0
    assert "Standard photographic metadata" in res["summary"]

def test_synthid_tier1_marker_detection():
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20 + b"Google DeepMind SynthID watermark marker" + b"\x00" * 30
    res = SynthIDService.inspect_metadata_and_bytes(data)
    
    assert res["is_synthetic"] is True
    assert res["synthid_detected"] is True
    assert any("SynthID" in g for g in res["detected_generators"])
    assert res["provenance_score"] >= 0.65

def test_synthid_tier1_png_exif_metadata():
    img = Image.new("RGB", (32, 32), color="purple")
    png_info = PngImagePlugin.PngInfo()
    png_info.add_text("parameters", "photorealistic luxury watch, synthid embedded watermark")
    png_info.add_text("Software", "Google DeepMind Imagen 3 SynthID")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG", pnginfo=png_info)
    res = SynthIDService.inspect_metadata_and_bytes(buf.getvalue())
    
    assert res["is_synthetic"] is True
    assert res["synthid_detected"] is True
    assert res["provenance_score"] >= 0.65

def test_synthid_tier3_vertex_ai_adapter():
    adapter = SynthIDService.inspect_vertex_ai_adapter()
    assert "provider" in adapter
    assert "Google Cloud Vertex AI SynthID" in adapter["provider"]
    assert adapter["status"] in ("configured", "unconfigured")

@pytest.mark.asyncio
async def test_synthid_unified_pipeline_clean():
    img = Image.new("RGB", (32, 32), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    
    res = await synthid_service.analyze_provenance(buf.getvalue())
    assert isinstance(res, dict)
    assert res["is_synthetic"] is False
    assert res["synthid_detected"] is False
    assert "No synthetic AI markers detected" in res["summary"]

@pytest.mark.asyncio
async def test_synthid_unified_pipeline_with_gemini_vision_mock():
    img = Image.new("RGB", (32, 32), color="yellow")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    
    mock_gemini_response = {
        "is_synthetic": True,
        "synthetic_confidence": 0.94,
        "synthid_detected": True,
        "detected_generator": "Imagen / SynthID",
        "visual_forensic_artifacts": ["diffusion pixel smoothing", "imperceptible high-frequency watermark"],
        "explanation": "Google DeepMind SynthID digital watermark identified with high neural confidence."
    }
    
    with patch.object(SynthIDService, "inspect_with_gemini_vision", new=AsyncMock(return_value=mock_gemini_response)):
        res = await synthid_service.analyze_provenance(buf.getvalue())
        assert res["is_synthetic"] is True
        assert res["synthid_detected"] is True
        assert res["provenance_score"] >= 0.90
        assert res["active_tier"] == "tier2_gemini_vision"
        assert "Google DeepMind SynthID watermark detected" in res["summary"]
