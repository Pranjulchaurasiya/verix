# Verix Invariant & Ground-Truth Benchmark Report

**Benchmark Generated:** 2026-10-08T23:46:57.478636+00:00  
**Evaluation Pass Rate:** **100.0%** (7/7 Scenarios Passed)  
**Mean Execution Latency:** **10.86 ms**  
**Invariant Violations:** **0**

---

## Benchmark Scenario Matrix

| ID | Evaluation Scope | Status | Latency | Key Assertion |
|---|---|---|---|---|
| `TC-01-WHITELIST` | Platform Whitelist Precision & Registry Integrity | **PASS** | 0.1 ms | Tested 3 trusted and 2 untrusted domains. |
| `TC-02-PRICING-ANOMALY` | Multi-Retailer Pricing Dispersion & Bait-and-Switch Counterfeit Detection | **PASS** | 0.19 ms | Median: $120.0 USD, Outliers Detected: 1 |
| `TC-03-AI-PROVENANCE` | Synthetic AI Generator Signatures & C2PA Provenance Detection | **PASS** | 58.73 ms | Detected generators: ['ComfyUI', 'Midjourney'], C2PA: True |
| `TC-04-CRYPTO-MERKLE` | RFC 8032 Ed25519 Signing & Merkle Inclusion Proof Integrity | **PASS** | 0.57 ms | Root: d0d78e4044eeef60..., Sig Valid: True, Proofs Valid: True |
| `TC-05-CLI-VERIFIER` | Third-Party Offline CLI Evidence Verification | **PASS** | 16.16 ms | CLI Verification Pass: True, Leaves Verified: 4 |
| `TC-06-SELLER-TAKEDOWN` | Seller Asset Protection & Statutory DMCA/VeRO Notice Compilation | **PASS** | 0.21 ms | Notice Case ID: VERIX-BENCH-SC, Infringing Count: 1 |
| `TC-07-WEBHOOKS` | Enterprise Webhook HMAC-SHA256 Signatures & Replay Prevention | **PASS** | 0.07 ms | Signature Valid: True, Tamper Rejected: True, Replay Prevented: True |

---

## Subsystem Invariant Summary

1. **Zero Hallucination Guarantee:** Decision bounds, Merkle tree construction, and price dispersion calculations are 100% deterministic with 0 LLM hallucinations in the mathematical path.
2. **Cryptographic Non-Repudiation:** All audit dossiers are signed via RFC 8032 Ed25519 digital signatures and anchored via binary Merkle Trees.
3. **Independent Third-Party Verification:** Evaluators can verify any dossier offline via `python verify_evidence_cli.py <path_to_dossier.json>`.
