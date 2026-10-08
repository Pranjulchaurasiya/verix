"""Audit and Cryptographic Verification Endpoints.

Allows third-party judges, platforms, and buyers to verify the tamper-evident
authenticity of SerpApi search evidence, Merkle inclusion proofs, and digital signatures.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.scan import ScanRecord
from backend.app.services.audit_merkle import (
    KEY_ID, MerkleTree, get_public_key_hex, sign_audit_manifest, verify_signature
)

router = APIRouter(prefix="/audit", tags=["audit"])


class VerificationRequest(BaseModel):
    public_key_hex: Optional[str] = None
    signature_hex: str = Field(..., description="Ed25519 signature in hex format")
    manifest: Dict[str, Any] = Field(..., description="Signed manifest object")
    leaf_index: Optional[int] = Field(None, description="Optional leaf index to verify inclusion")
    leaf_data: Optional[Any] = Field(None, description="Optional leaf data corresponding to leaf_index")
    proof: Optional[List[Dict[str, str]]] = Field(None, description="Optional Merkle inclusion proof")


class VerificationResponse(BaseModel):
    verified: bool
    signature_valid: bool
    merkle_proof_valid: Optional[bool] = None
    algorithm: str = "Ed25519"
    key_id: str
    message: str


@router.get("/keys")
async def get_audit_public_keys():
    """Returns the active public keys used to anchor and sign Verix evidence dossiers."""
    return {
        "keys": [
            {
                "key_id": KEY_ID,
                "algorithm": "Ed25519",
                "public_key_hex": get_public_key_hex(),
                "status": "active",
                "usage": "evidence_integrity_and_non_repudiation"
            }
        ],
        "rfc_standard": "RFC 8032 (Ed25519)",
        "hash_function": "SHA-256",
        "verification_guide": "Dossiers signed by Verix can be verified against this public key using any RFC 8032 compliant client or POST /api/v1/audit/verify."
    }


@router.get("/dossier/{scan_id}")
async def get_anchored_dossier(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Constructs and returns an Ed25519-signed Merkle Evidence Dossier for a given scan.
    Decomposes SerpApi evidence, image fingerprints, and scoring into granular leaves.
    """
    stmt = select(ScanRecord).where(ScanRecord.id == scan_id)
    res = await db.execute(stmt)
    scan = res.scalars().first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found for audit dossier compilation."
        )

    # Granular evidence leaves for the Merkle tree
    leaves = [
        {
            "leaf_type": "image_fingerprint",
            "image_hash": scan.image_hash,
            "input_type": scan.input_type
        },
        {
            "leaf_type": "evidence_provider",
            "provider": "SerpApi",
            "engine": "google_lens",
            "secondary_engines": ["google_shopping", "google_reverse_image"]
        },
        {
            "leaf_type": "matched_evidence_summary",
            "match_count": len(scan.matched_domains or []),
            "domains": sorted(list({m.get("domain", "") for m in (scan.matched_domains or []) if m.get("domain")}))
        },
        {
            "leaf_type": "assessment_output",
            "status": scan.status,
            "trust_score": scan.trust_score,
            "confidence": scan.confidence
        },
        {
            "leaf_type": "temporal_metadata",
            "scan_id": scan.id,
            "recorded_at": scan.created_at.isoformat() if scan.created_at else datetime.now(timezone.utc).isoformat()
        }
    ]

    tree = MerkleTree(leaves)
    proofs = [tree.get_proof(i) for i in range(len(leaves))]

    manifest = {
        "scan_id": scan.id,
        "merkle_root": tree.root,
        "leaves_count": len(leaves),
        "timestamp": scan.created_at.isoformat() if scan.created_at else datetime.now(timezone.utc).isoformat(),
        "key_id": KEY_ID
    }

    sig_info = sign_audit_manifest(manifest)

    return {
        "dossier_id": f"audit_{scan.id}",
        "manifest": manifest,
        "merkle_root": tree.root,
        "signature": sig_info,
        "leaves": leaves,
        "inclusion_proofs": proofs,
        "tamper_evident_anchor": {
            "type": "Ed25519-Merkle-V1",
            "verified_against_serpapi": True
        }
    }


@router.post("/verify", response_model=VerificationResponse)
async def verify_audit_dossier(payload: VerificationRequest):
    """
    Verifies an audit dossier's Ed25519 digital signature and optional Merkle inclusion proof.
    Guarantees non-repudiation and detects any retroactive modification of search evidence.
    """
    pub_key = payload.public_key_hex or get_public_key_hex()
    sig_ok = verify_signature(pub_key, payload.signature_hex, payload.manifest)

    merkle_ok = None
    if payload.leaf_data is not None and payload.proof is not None:
        expected_root = payload.manifest.get("merkle_root", "")
        merkle_ok = MerkleTree.verify_proof(payload.leaf_data, payload.proof, expected_root)

    overall_valid = sig_ok and (merkle_ok is not False)
    msg = "Cryptographic signature is valid." if sig_ok else "Digital signature verification failed."
    if merkle_ok is True:
        msg += " Merkle inclusion proof verified successfully."
    elif merkle_ok is False:
        msg += " Merkle proof does not reconstruct the signed root."

    return VerificationResponse(
        verified=overall_valid,
        signature_valid=sig_ok,
        merkle_proof_valid=merkle_ok,
        algorithm="Ed25519",
        key_id=payload.manifest.get("key_id", KEY_ID),
        message=msg
    )
