"""Verifiable Merkle Tree and Ed25519 Cryptographic Evidence Anchoring Service.

Provides third-party verifiable audit proofs over SerpApi search snapshots,
image perceptual hashes, and decision outputs. Anyone with Verix's public key
can verify that search evidence was captured at the recorded time and was not
altered or tampered with retroactively.
"""

from typing import List, Dict, Any, Optional, Tuple
import hashlib
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Consistent Key ID for the current deployment
KEY_ID = "verix-ed25519-anchor-v1"

# Persistent/reproducible server keypair for development & hackathon demonstration
# Seeded deterministically so restart retains verifiable consistency
_SEED = hashlib.sha256(b"verix-evidence-anchor-secret-seed-2026").digest()
_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(_SEED)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()


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


class MerkleTree:
    """Binary Merkle Tree supporting cryptographic inclusion proofs."""

    def __init__(self, leaves: List[Any]):
        if not leaves:
            self.leaf_hashes: List[str] = [hashlib.sha256(b"").hexdigest()]
        else:
            self.leaf_hashes = [hash_leaf(leaf) for leaf in leaves]
        self.levels: List[List[str]] = [self.leaf_hashes]
        self._build_tree()

    def _build_tree(self):
        current = self.leaf_hashes
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else current[i]
                combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
                next_level.append(combined)
            self.levels.append(next_level)
            current = next_level

    @property
    def root(self) -> str:
        """Returns hex-encoded Merkle root."""
        return self.levels[-1][0]

    def get_proof(self, index: int) -> List[Dict[str, str]]:
        """Returns the sibling path necessary to prove leaf inclusion."""
        if index < 0 or index >= len(self.leaf_hashes):
            raise IndexError("Leaf index out of bounds")

        proof: List[Dict[str, str]] = []
        current_index = index

        for level in self.levels[:-1]:
            is_right_child = (current_index % 2 == 1)
            sibling_index = current_index - 1 if is_right_child else current_index + 1

            if sibling_index < len(level):
                sibling_hash = level[sibling_index]
            else:
                sibling_hash = level[current_index]

            proof.append({
                "position": "left" if is_right_child else "right",
                "hash": sibling_hash
            })
            current_index = current_index // 2

        return proof

    @staticmethod
    def verify_proof(leaf_data: Any, proof: List[Dict[str, str]], expected_root: str) -> bool:
        """Verifies whether leaf_data reconstructs expected_root given proof path."""
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


def get_public_key_hex() -> str:
    """Returns the Ed25519 public key as raw hex."""
    raw_bytes = _PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return raw_bytes.hex()


def sign_audit_manifest(manifest_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Signs canonical manifest bytes using Ed25519 private key."""
    canonical_bytes = canonical_json(manifest_payload)
    signature = _PRIVATE_KEY.sign(canonical_bytes)
    return {
        "key_id": KEY_ID,
        "algorithm": "Ed25519",
        "public_key_hex": get_public_key_hex(),
        "signature_hex": signature.hex(),
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "payload_digest": hashlib.sha256(canonical_bytes).hexdigest()
    }


def verify_signature(public_key_hex: str, signature_hex: str, manifest_payload: Dict[str, Any]) -> bool:
    """Verifies that manifest_payload was signed by the Ed25519 key."""
    try:
        pub_bytes = bytes.fromhex(public_key_hex)
        sig_bytes = bytes.fromhex(signature_hex)
        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        canonical_bytes = canonical_json(manifest_payload)
        pub_key.verify(sig_bytes, canonical_bytes)
        return True
    except (ValueError, InvalidSignature, Exception):
        return False
