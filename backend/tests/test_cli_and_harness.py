import os
import pytest
from verify_evidence_cli import verify_dossier
from evaluate_ground_truth import run_benchmark_suite
from backend.app.services.audit_merkle import MerkleTree, sign_audit_manifest

def test_cli_verification_with_tampering():
    leaves = [{"evidence": "item_1"}, {"evidence": "item_2"}]
    tree = MerkleTree(leaves)
    manifest = {
        "scan_id": "cli-test-uuid",
        "merkle_root": tree.root,
        "timestamp": "2026-10-08T00:00:00Z"
    }
    sig = sign_audit_manifest(manifest)

    dossier = {
        "dossier_id": "test_dossier_01",
        "manifest": manifest,
        "merkle_root": tree.root,
        "signature": sig,
        "leaves": leaves,
        "inclusion_proofs": [tree.get_proof(i) for i in range(len(leaves))]
    }

    temp_path = "temp_cli_test_dossier.json"
    import json
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(dossier, f)

    try:
        # Valid dossier
        res = verify_dossier(temp_path)
        assert res["valid"] is True
        assert res["signature_valid"] is True
        assert res["merkle_valid"] is True
        assert res["proofs_checked"] == 2

        # Tampered dossier (change leaf content)
        dossier["leaves"][0] = {"evidence": "tampered_item_1"}
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(dossier, f)

        res_tampered = verify_dossier(temp_path)
        assert res_tampered["valid"] is False
        assert res_tampered["merkle_valid"] is False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_ground_truth_benchmark_harness():
    report = run_benchmark_suite()
    assert report["total_tests"] == 7
    assert report["passed_tests"] == 7
    assert report["pass_rate_pct"] == 100.0
    assert report["invariants_violated"] == 0

