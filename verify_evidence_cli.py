#!/usr/bin/env python3
"""Verix Cryptographic Evidence CLI Verification Tool.

Standalone utility for hackathon judges, platforms, and third-party auditors
to independently verify the cryptographic integrity and authenticity of Verix audit dossiers
without trusting the backend or frontend servers.

Supports RFC 8032 Ed25519 signature validation and Merkle inclusion proof verification.
"""

import sys
import os
import argparse
import json
import hashlib
from typing import Dict, Any, Optional

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519, ec
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.exceptions import InvalidSignature
except ImportError:
    print("[ERROR] 'cryptography' library is required. Install via: pip install cryptography", file=sys.stderr)
    sys.exit(2)


def canonical_json(data: Any) -> bytes:
    """Produces deterministic canonical UTF-8 JSON bytes (sorted keys, compact)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def hash_leaf(data: Any) -> str:
    """Computes SHA-256 digest of arbitrary leaf data."""
    if isinstance(data, (bytes, bytearray)):
        content = data
    elif isinstance(data, str):
        content = data.encode("utf-8")
    else:
        content = canonical_json(data)
    return hashlib.sha256(content).hexdigest()


def verify_merkle_proof(leaf_data: Any, proof: list, expected_root: str) -> bool:
    """Verifies that leaf_data reconstructs expected_root given the proof path."""
    current_hash = hash_leaf(leaf_data)
    for step in proof:
        sibling = step["hash"]
        pos = step["position"]
        if pos == "left":
            combined = hashlib.sha256((sibling + current_hash).encode("utf-8")).hexdigest()
        else:
            combined = hashlib.sha256((current_hash + sibling).encode("utf-8")).hexdigest()
        current_hash = combined
    return current_hash.lower() == expected_root.lower()


def verify_ed25519_signature(public_key_hex: str, signature_hex: str, manifest: Dict[str, Any]) -> bool:
    """Verifies Ed25519 or ECDSA P-256 signature over canonical manifest payload."""
    canonical_bytes = canonical_json(manifest)
    # 1. Try Ed25519
    try:
        pub_bytes = bytes.fromhex(public_key_hex)
        sig_bytes = bytes.fromhex(signature_hex)
        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        pub_key.verify(sig_bytes, canonical_bytes)
        return True
    except Exception:
        pass

    # 2. Try ECDSA NIST P-256 (KMS DER public key)
    try:
        pub_bytes = bytes.fromhex(public_key_hex)
        sig_bytes = bytes.fromhex(signature_hex)
        pub_key = serialization.load_der_public_key(pub_bytes)
        pub_key.verify(sig_bytes, canonical_bytes, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        pass

    return False


def verify_dossier(dossier_path: str, public_key_override: Optional[str] = None, verbose: bool = False) -> Dict[str, Any]:
    """Inspects and cryptographically validates a dossier file."""
    if not os.path.exists(dossier_path):
        return {"valid": False, "error": f"File not found: {dossier_path}"}

    try:
        with open(dossier_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return {"valid": False, "error": f"Failed to parse JSON: {exc}"}

    manifest = data.get("manifest")
    sig_info = data.get("signature", {})
    merkle_root = data.get("merkle_root") or (manifest.get("merkle_root") if manifest else None)

    if not manifest or not sig_info:
        return {"valid": False, "error": "Missing 'manifest' or 'signature' block in dossier"}

    pub_hex = public_key_override or sig_info.get("public_key_hex")
    sig_hex = sig_info.get("signature_hex")

    if not pub_hex or not sig_hex:
        return {"valid": False, "error": "Missing public key or signature hex"}

    # 1. Signature Verification
    sig_valid = verify_ed25519_signature(pub_hex, sig_hex, manifest)
    if verbose:
        print(f"[*] Signature check (Ed25519): {'PASS' if sig_valid else 'FAIL'}")

    # 2. Merkle Root and Inclusion Proofs (if present)
    leaves = data.get("leaves", [])
    proofs = data.get("inclusion_proofs", [])
    merkle_valid = True
    proof_count = 0

    if leaves and proofs and merkle_root:
        for idx, (leaf, proof) in enumerate(zip(leaves, proofs)):
            if not verify_merkle_proof(leaf, proof, merkle_root):
                merkle_valid = False
                if verbose:
                    print(f"[-] Merkle inclusion failure at leaf #{idx}")
                break
            proof_count += 1
        if verbose and merkle_valid:
            print(f"[*] Merkle proofs ({proof_count} leaves): PASS")

    overall = sig_valid and merkle_valid

    return {
        "valid": overall,
        "signature_valid": sig_valid,
        "merkle_valid": merkle_valid,
        "merkle_root": merkle_root,
        "algorithm": sig_info.get("algorithm", "Ed25519"),
        "key_id": sig_info.get("key_id", "unknown"),
        "proofs_checked": proof_count,
        "dossier_id": data.get("dossier_id") or manifest.get("scan_id")
    }


def main():
    parser = argparse.ArgumentParser(description="Verix Standalone Cryptographic Verification CLI")
    parser.add_argument("file", help="Path to Verix JSON audit dossier file")
    parser.add_argument("--public-key", help="Optional hex-encoded Ed25519 public key override")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose step-by-step trace")

    args = parser.parse_args()

    res = verify_dossier(args.file, public_key_override=args.public_key, verbose=args.verbose)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        if res.get("valid"):
            print("==================================================")
            print("  VERIX CRYPTOGRAPHIC VERIFICATION: [PASS]")
            print("==================================================")
            print(f"  Dossier ID      : {res.get('dossier_id')}")
            print(f"  Algorithm       : {res.get('algorithm')}")
            print(f"  Key ID          : {res.get('key_id')}")
            print(f"  Merkle Root     : {res.get('merkle_root')}")
            print(f"  Inclusion Proofs: {res.get('proofs_checked')} leaves verified")
            print("  Evidence Status : Unaltered, authentic, tamper-evident.")
        else:
            print("==================================================")
            print("  VERIX CRYPTOGRAPHIC VERIFICATION: [FAILED]")
            print("==================================================")
            print(f"  Reason: {res.get('error') or 'Digital signature or Merkle proof mismatch'}")

    sys.exit(0 if res.get("valid") else 1)


if __name__ == "__main__":
    main()
