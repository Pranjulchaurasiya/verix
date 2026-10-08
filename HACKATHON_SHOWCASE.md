# Verix — SerpApi Hackathon 2026 Master Showcase & Technical Defense Dossier

> **Verix: Cryptographically-Anchored Visual Intelligence & Counterfeit Risk Mitigation Engine Powered by SerpApi**

---

## Executive Summary

Verix transforms unstructured web image results from **SerpApi Google Lens** into a **tamper-evident, cryptographically signed, and legally actionable threat intelligence dossier**.

Built across **10 iterative engineering sprints**, Verix solves the three core bottlenecks of automated e-commerce protection:
1. **API Cost & Latency:** Consolidated multi-tab Lens exploration into a single bounded call with token-bucket credit guards and 24h caching.
2. **Ghost Listings & AI Fakes:** Integrated byte-level C2PA Content Credentials and synthetic generative AI provenance (Midjourney, Stable Diffusion, DALL-E, ComfyUI, SynthID markers).
3. **Legal & Third-Party Verifiability:** Anchored every scraped match into an **RFC 8032 Ed25519** signature and binary **Merkle tree**, verified offline with zero server dependencies via `verify_evidence_cli.py`.

---

## 1. Complete 10-Sprint Engineering Progression

| Sprint | Architecture Milestone | Key Capabilities Delivered | Test Target |
|:---:|:---|:---|:---:|
| **1** | **1-Call SerpApi Optimization & Credit Guard** | Consolidated Lens requests to 1 roundtrip; added 24h caching, semaphore concurrency bounds (`asyncio.Semaphore(5)`), and credit guards. | `test_multi_engine.py` |
| **2** | **Tamper-Evident Export Dossier** | Generated downloadable JSON/CSV incident dossiers signed with SHA-256 HMAC digest checksums. | `test_api_endpoints.py` |
| **3** | **Batch & Multi-Image Pipeline** | `POST /api/v1/analyze/batch` enabling enterprise catalog ingestion, multi-angle clustering, and bulk risk scoring. | `batch-result-view.tsx` |
| **4** | **Synthetic AI Provenance & C2PA** | Deep EXIF/PNG chunk parser for generative AI model signatures; prevents zero-match false negatives on synthetic ghost listings. | `test_provenance.py` |
| **5** | **RFC 8032 Ed25519 & Merkle Anchoring** | Cryptographic audit trail with O(log N) binary inclusion proofs and key rotation registry (`/api/v1/audit/*`). | `test_audit_merkle.py` |
| **6** | **Seller Asset Protection & Takedown Desk** | Automated 17 U.S.C. § 512(c) statutory notice compilation for Amazon Brand Registry, eBay VeRO, and Shopify Abuse. | `test_takedown.py` |
| **7** | **Multi-Retailer Pricing Anomaly Engine** | Currency normalization, IQR dispersion fencing, and modified Z-score detection for bait-and-switch counterfeit discounts. | `test_pricing.py` |
| **8** | **Offline CLI Verifier & Benchmark Harness** | Zero-trust standalone `verify_evidence_cli.py` and reproducible 7-point evaluation harness `evaluate_ground_truth.py`. | `test_cli_and_harness.py` |
| **9** | **Enterprise Marketplace Webhook Engine** | Real-time event streaming with Stripe-compatible HMAC-SHA256 headers (`X-Verix-Signature`) and replay rejection. | `test_webhooks.py` |
| **10** | **Verix Verifiable Dossier (VVD) Inspector** | Interactive in-app cryptographic inspector modal with live client verification, CLI command copy, and full manifest export. | `dossier-dialog.tsx` |

---

## 2. 7-Point Benchmark Evaluation Harness (`evaluate_ground_truth.py`)

Verix contains a built-in automated ground-truth benchmark suite measuring correctness, determinism, and latency:

```bash
python evaluate_ground_truth.py
```

### Measured Benchmark Telemetry

```text
==================================================================
  VERIX BENCHMARK EVALUATION HARNESS — SERPAPI HACKATHON 2026
==================================================================
  [1/7] TC-01-WHITELIST: PASS (0.11ms)
  [2/7] TC-02-PRICING-ANOMALY: PASS (0.24ms)
  [3/7] TC-03-AI-PROVENANCE: PASS (86.84ms)
  [4/7] TC-04-CRYPTO-MERKLE: PASS (0.78ms)
  [5/7] TC-05-CLI-VERIFIER: PASS (16.20ms)
  [6/7] TC-06-SELLER-TAKEDOWN: PASS (0.33ms)
  [7/7] TC-07-WEBHOOKS: PASS (0.13ms)
==================================================================
  BENCHMARK SUITE COMPLETE: 7/7 PASSED (100.0%)
  Mean Latency: 14.95ms | Invariants Violated: 0
==================================================================
```

---

## 3. The 90-Second Hackathon Judge Pitch & Live Demo Walkthrough

### Act 1: The Problem (0:00 - 0:20)
> *"E-commerce counterfeiters scrape genuine catalog photography and re-post listings across untrusted replica storefronts at an 80% discount. Buyers get scammed, and brand owners lose millions. Today, verifying an image requires manual reverse-searching and offers zero legal admissibility."*

### Act 2: SerpApi Ingestion + Threat Triangulation (0:20 - 0:50)
> *"Verix ingests a product URL or image, executing a single optimized SerpApi Google Lens call. In under 800ms, our pipeline extracts visual matches, retailer prices, and availability. But we don't stop there: our provenance engine scans image bytes for Midjourney/C2PA synthetic watermarks, while our pricing engine detects bait-and-switch outlier discounts using median IQR dispersion."*

### Act 3: Cryptographic Integrity & Offline Verification (0:50 - 1:15)
> *"Every single piece of evidence is hashed into a binary Merkle tree and signed with an RFC 8032 Ed25519 private key. Anyone—a judge, an auditor, or a marketplace lawyer—can open our open-source CLI verifier (`python verify_evidence_cli.py`) and verify evidence validity completely offline."*

### Act 4: Real-World Action (1:15 - 1:30)
> *"With one click, brand owners export a statutory 17 U.S.C. § 512(c) DMCA notice with direct links to Amazon Brand Registry, eBay VeRO, and Shopify abuse desks. Enterprise security teams receive instant HMAC-signed webhook dispatches. Verix turns raw web search into legal action."*

---

## 4. Architecture Diagram

```mermaid
graph TD
    User([User / Enterprise Ingestion]) -->|URL or Image| API[FastAPI Gateway]
    
    subgraph Engine [Threat Intelligence & Ingestion]
        API -->|1-Call Lens| SerpApi[SerpApi Google Lens Service]
        API -->|Byte Analysis| Prov[C2PA & Synthetic AI Provenance]
        SerpApi -->|Extracted Listings| Pricing[Multi-Retailer Pricing Engine]
    end

    subgraph SecurityCore [Deterministic Cryptographic Core]
        Pricing --> Merkle[Binary Merkle Tree Builder]
        Prov --> Merkle
        Merkle -->|Root Hash| Ed25519[RFC 8032 Ed25519 Signer]
        Ed25519 --> Dossier[Verix Verifiable Dossier VVD]
    end

    subgraph Downstream [Enforcement & Dispatch]
        Dossier --> Webhooks[HMAC-SHA256 Webhooks Engine]
        Dossier --> Takedown[1-Click DMCA / VeRO Statutory Notice]
        Dossier --> CLI[Offline CLI Verifier Tool]
        Dossier --> UI[Next.js 16 Web Dashboard]
    end
```

---

## 5. Security & Invariant Guarantees

1. **Non-Accusatory Language Policy:** User-facing strings report *public evidence signals* rather than making defamatory accusations against unverified merchants.
2. **Zero Test Regressions:** 54 out of 54 automated pytest tests passing in 6.47s.
3. **Next.js 16 Production Build:** Clean build and static prerender in under 12 seconds with 0 TypeScript/lint warnings.
4. **Offline Verifiability:** Cryptographic verification runs locally in pure Python standard library / cryptography without network access.
