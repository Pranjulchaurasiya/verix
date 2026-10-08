import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.takedown import generate_takedown_package
from backend.app.services.audit_merkle import verify_signature, get_public_key_hex

def test_generate_takedown_package_structure():
    matched = [
        {"domain": "unauthorized-shop.com", "link": "https://unauthorized-shop.com/product/123", "is_whitelisted": False, "title": "Cheap Replica Sneaker"},
        {"domain": "amazon.com", "link": "https://amazon.com/dp/B001", "is_whitelisted": True, "title": "Official Listing"}
    ]
    pkg = generate_takedown_package(
        scan_id="scan-uuid-5678",
        image_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        matched_domains=matched,
        claimant_name="Nike Brand Protection Team",
        product_title="Air Jordan 1 Retro High OG"
    )

    assert pkg["case_id"].startswith("VERIX-")
    assert pkg["claimant_name"] == "Nike Brand Protection Team"
    assert pkg["infringing_count"] == 1
    assert pkg["infringing_items"][0]["domain"] == "unauthorized-shop.com"
    assert "17 U.S.C. § 512(c)" in pkg["notice_text"]
    assert "Nike Brand Protection Team" in pkg["notice_text"]
    assert "Ed25519 Evidence Signature" in pkg["notice_text"]

    # Verify that the signature is valid
    pub_hex = get_public_key_hex()
    sig_hex = pkg["signature"]["signature_hex"]
    manifest = {
        "scan_id": "scan-uuid-5678",
        "merkle_root": pkg["merkle_root"],
        "type": "DMCA_TAKEDOWN_EVIDENCE_V1",
        "timestamp": pkg["created_at"]
    }
    assert verify_signature(pub_hex, sig_hex, manifest) is True

@pytest.mark.asyncio
async def test_enforce_takedown_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Non-existent scan should return 404
        resp = await client.get("/api/v1/enforce/takedown/non-existent-scan-id")
        assert resp.status_code == 404
