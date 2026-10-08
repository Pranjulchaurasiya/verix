import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.audit_merkle import (
    MerkleTree, get_public_key_hex, sign_audit_manifest, verify_signature, canonical_json
)

def test_merkle_tree_construction_and_verification():
    leaves = [
        {"item": "photo_1", "hash": "abc123"},
        {"item": "photo_2", "hash": "def456"},
        {"item": "photo_3", "hash": "ghi789"},
    ]
    tree = MerkleTree(leaves)
    assert tree.root is not None
    assert len(tree.root) == 64

    # Verify proof for leaf 0
    proof0 = tree.get_proof(0)
    assert len(proof0) > 0
    assert MerkleTree.verify_proof(leaves[0], proof0, tree.root) is True

    # Tampered leaf must fail verification
    tampered_leaf = {"item": "photo_1", "hash": "TAMPERED"}
    assert MerkleTree.verify_proof(tampered_leaf, proof0, tree.root) is False

    # Proof for leaf 2 (odd-index branch)
    proof2 = tree.get_proof(2)
    assert MerkleTree.verify_proof(leaves[2], proof2, tree.root) is True

def test_ed25519_signature_and_verification():
    manifest = {
        "scan_id": "test-uuid-1234",
        "merkle_root": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "timestamp": "2026-10-08T00:00:00Z"
    }
    sig_info = sign_audit_manifest(manifest)
    assert sig_info["algorithm"] == "Ed25519"
    pub_hex = sig_info["public_key_hex"]
    sig_hex = sig_info["signature_hex"]

    # Verify signature
    assert verify_signature(pub_hex, sig_hex, manifest) is True

    # Tampered manifest must fail verification
    tampered_manifest = dict(manifest)
    tampered_manifest["merkle_root"] = "tampered_root"
    assert verify_signature(pub_hex, sig_hex, tampered_manifest) is False

@pytest.mark.asyncio
async def test_audit_public_keys_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/audit/keys")
        assert resp.status_code == 200
        data = resp.json()
        assert "keys" in data
        assert len(data["keys"]) > 0
        assert data["keys"][0]["algorithm"] == "Ed25519"
        assert len(data["keys"][0]["public_key_hex"]) == 64

@pytest.mark.asyncio
async def test_audit_verify_endpoint():
    manifest = {
        "scan_id": "demo-scan-001",
        "merkle_root": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "timestamp": "2026-10-08T04:00:00Z"
    }
    sig_info = sign_audit_manifest(manifest)

    leaf = {"evidence": "serpapi_lens_verified", "matches": 4}
    tree = MerkleTree([leaf])
    proof = tree.get_proof(0)

    # Update manifest to use actual root
    manifest["merkle_root"] = tree.root
    sig_info = sign_audit_manifest(manifest)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "public_key_hex": sig_info["public_key_hex"],
            "signature_hex": sig_info["signature_hex"],
            "manifest": manifest,
            "leaf_index": 0,
            "leaf_data": leaf,
            "proof": proof
        }
        resp = await client.post("/api/v1/audit/verify", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is True
        assert data["signature_valid"] is True
        assert data["merkle_proof_valid"] is True
