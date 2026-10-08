import pytest
import io
from PIL import Image, PngImagePlugin
from backend.app.services.provenance import analyze_image_provenance

def test_provenance_empty_or_corrupt():
    res1 = analyze_image_provenance(None)
    assert res1["is_synthetic"] is False
    assert res1["has_provenance_data"] is False

    res2 = analyze_image_provenance(b"tiny_bytes")
    assert res2["is_synthetic"] is False

def test_provenance_c2pa_detection():
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20 + b"urn:c2pa:content_credentials" + b"\x00" * 50
    res = analyze_image_provenance(data)
    assert res["c2pa_present"] is True
    assert "C2PA" in res["summary"]

def test_provenance_raw_generator_detection():
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 30 + b"Stable Diffusion model generation comfyui" + b"\x00" * 50
    res = analyze_image_provenance(data)
    assert res["is_synthetic"] is True
    assert any("Stable Diffusion" in g or "ComfyUI" in g for g in res["detected_generators"])

def test_provenance_pillow_png_metadata():
    img = Image.new("RGB", (32, 32), color="red")
    png_info = PngImagePlugin.PngInfo()
    png_info.add_text("parameters", "photorealistic Nike sneaker, highly detailed, 8k resolution, midjourney v6")
    png_info.add_text("Software", "Midjourney")

    buf = io.BytesIO()
    img.save(buf, format="PNG", pnginfo=png_info)
    img_bytes = buf.getvalue()

    res = analyze_image_provenance(img_bytes)
    assert res["is_synthetic"] is True
    assert "Midjourney" in res["detected_generators"]
    assert res["provenance_score"] > 0.6
    assert "Synthetic generation signature detected" in res["summary"]

def test_provenance_clean_camera_image():
    img = Image.new("RGB", (32, 32), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    res = analyze_image_provenance(img_bytes)
    assert res["is_synthetic"] is False
    assert len(res["detected_generators"]) == 0
