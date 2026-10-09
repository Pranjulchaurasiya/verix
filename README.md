# Verix — Cryptographically-Anchored Visual Intelligence & Counterfeit Risk Mitigation Engine

[![CI/CD Pipeline](https://github.com/Pranjulchaurasiya/Verix/actions/workflows/ci.yml/badge.svg)](https://github.com/Pranjulchaurasiya/Verix/actions/workflows/ci.yml)
[![Tests Passing](https://img.shields.io/badge/pytest-61%2F61%20passed-brightgreen.svg)](BENCHMARK_REPORT.md)
[![Ground Truth Benchmark](https://img.shields.io/badge/Benchmark%20Pass%20Rate-100%25%20(7%2F7)-emerald.svg)](benchmark_report.json)
[![Cryptography](https://img.shields.io/badge/Integrity-AWS%20KMS%20HSM%20%2B%20Merkle-purple.svg)](verify_evidence_cli.py)
[![Live Web App](https://img.shields.io/badge/Vercel-Live%20Web%20App-000000.svg?logo=vercel&logoColor=white)](https://verix-via-serpapi.vercel.app/)
[![Live Backend](https://img.shields.io/badge/Render-Live%20Backend-46e3b7.svg)](https://verix-t4a1.onrender.com)
[![YouTube Demo](https://img.shields.io/badge/YouTube-Product%20Demo%20(27s)-red?logo=youtube)](https://youtu.be/XGYe5E_hoCo)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.3.3%20Turbopack-black.svg)](https://nextjs.org/)

Verix is an enterprise-grade visual intelligence engine engineered to detect unauthorized product photo reuse, bait-and-switch counterfeit pricing anomalies, and synthetic generative AI listings. Powered by a **4-Tier SerpApi Engine Suite** (**Google Lens**, **Google Shopping**, **Google Search**, and **YouTube**), Verix crawls public marketplaces, extracts visual matches, benchmarks MSRP ranges across authorized distributors, audits storefront domain reputation, and anchors all harvested evidence into an immutable, cryptographically verifiable audit package.

> 🌐 **Live Production Deployments**:
> * **Live Web Application (Vercel)**: [https://verix-via-serpapi.vercel.app](https://verix-via-serpapi.vercel.app)
> * **Backend API (Render)**: [https://verix-t4a1.onrender.com](https://verix-t4a1.onrender.com)
> * **Interactive API Documentation (Swagger)**: [https://verix-t4a1.onrender.com/docs](https://verix-t4a1.onrender.com/docs)
> * **Public AWS KMS Key Registry**: [https://verix-t4a1.onrender.com/api/v1/audit/keys](https://verix-t4a1.onrender.com/api/v1/audit/keys)
> * **GitHub Repository**: [https://github.com/Pranjulchaurasiya/Verix](https://github.com/Pranjulchaurasiya/Verix)

---

## 🎬 Video Overview & Commercial Demo

[![Verix Product Demo](https://img.youtube.com/vi/XGYe5E_hoCo/maxresdefault.jpg)](https://youtu.be/XGYe5E_hoCo)

> 📺 **[Watch on YouTube: Never Get Scammed Shopping Online Again — Verix Visual Intelligence Demo](https://youtu.be/XGYe5E_hoCo)**

---

## User Interface & Console

### 1. Visual Verification Console
The primary investigation dashboard provides real-time image uploads or product URL crawling, multi-engine corroboration, price distribution fences, and 1-click verifiable dossiers.

![Verix Visual Verification Console](docs/images/verix_console_ui.png)

### 2. Cryptographic Scan History & Evidence Ledger
Every investigation is persisted with its unique perceptual hash, RFC 8032 Ed25519 digital signature, and Merkle root proof for audit compliance.

![Verix Scan History](docs/images/verix_history_ui.png)

### 3. System Operations & Platform Telemetry
Live telemetry monitoring database connectivity, SerpApi rate limits, and whitelisted marketplace domains.

![Verix System Telemetry](docs/images/verix_system_ui.png)

---

## System Architecture

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion & Pre-flight Security"]
        A[Client: Image Upload or Marketplace URL] --> B{Input Type}
        B -->|Direct Image| C[Format & Pixel Dimension Validation]
        B -->|Storefront URL| D[SSRF Firewall & DNS IP Resolution]
        D --> E[DOM & JSON-LD Image Extractor]
        E --> F[Perceptual pHash & SHA-256 Hasher]
        C --> F
    end

    subgraph Intelligence["2. Multi-Engine Visual Intelligence"]
        F --> G[SerpApi Google Lens Visual Index]
        G --> H[Multi-Engine Corroboration: Shopping & Web]
        H --> I[Distinct Host Domain Accumulator]
    end

    subgraph Guardrails["3. Deterministic Risk & Provenance Core"]
        I --> J{Sufficient Evidence?<br/>Distinct Domains >= 2}
        J -->|No| K[Fail-Closed Safe Exit: Score = None]
        J -->|Yes| L[Multi-Retailer Pricing Anomaly Engine]
        L --> M[Synthetic AI & C2PA Provenance Scanner]
        M --> N[Platform Whitelist Registry Matcher]
        N --> O[Deterministic Heuristic Scoring Formula]
    end

    subgraph Cryptography["4. Cryptographic Anchoring & Delivery"]
        O --> P[RFC 8785 Canonical Serialization]
        P --> Q[Binary Merkle Tree Compilation]
        Q --> R[RFC 8032 Ed25519 Digital Signing]
        R --> S[Verix Verifiable Dossier .json / .csv]
        R --> T[Interactive Next.js 16 Console]
        R --> U[Standalone CLI Verifier verify_evidence_cli.py]
    end

    style Ingestion fill:#f8fafc,stroke:#3b82f6,stroke-width:2px
    style Intelligence fill:#f0fdf4,stroke:#22c55e,stroke-width:2px
    style Guardrails fill:#fff7ed,stroke:#f97316,stroke-width:2px
    style Cryptography fill:#faf5ff,stroke:#a855f7,stroke-width:2px
```

---

## Key Capabilities

1. **4-Tier SerpApi Visual & Market Intelligence Engine:**
   - **Google Lens (`google_lens`)**: Reverse-image perceptual retrieval across web marketplaces with token-based caching.
   - **Google Shopping (`google_shopping`)**: Live MSRP benchmark range, authorized distributor badges, delivery policies, and store pricing matrix.
   - **Google Search (`google`)**: Domain reputation footprint, consumer forum scam watchdogs, and merchant complaint auditing.
   - **YouTube Search (`youtube`)**: Video forensic unboxing guides and "Real vs Fake" side-by-side authenticity comparisons.
2. **RFC 8032 Ed25519 & Merkle Inclusion Proofs:**
   - Every harvested match and assessment output is compiled into a binary Merkle tree and digitally signed. Third parties can verify evidence offline via `verify_evidence_cli.py` with zero reliance on the backend server.
3. **Synthetic AI & C2PA Provenance Detection:**
   - Analyzes raw image bytes for C2PA Content Credentials and generative AI model signatures (Midjourney, Stable Diffusion, DALL-E, SynthID).
4. **Multi-Retailer Pricing Dispersion Analysis:**
   - Computes median market fences and flags severe counterfeit discounts (> 60% below median retail) indicating bait-and-switch listings.
5. **Strict Non-Accusatory Policy (Zero Slanderous Hallucinations):**
   - User-facing verdicts never make unsubstantiated assertions (`scam`, `fraud`, `fake`, `criminal`). Objective, evidence-based descriptions (`"unverified merchant domain"`, `"image appears on multiple sites"`) are strictly enforced.
6. **Fail-Closed Zero-Hallucination Safe Mode:**
   - If fewer than 2 distinct host domains are discovered, Verix returns `Score: None` and `"insufficient_data"` rather than fabricating an arbitrary score.
7. **Automated Statutory Takedown Generation:**
   - Generates 1-click statutory 17 U.S.C. § 512(c) DMCA / VeRO notices for Amazon Brand Registry, eBay VeRO, and Shopify Abuse.
8. **Enterprise Webhook Dispatcher:**
   - Real-time webhook notifications authenticated via Stripe-compatible HMAC-SHA256 signatures (`X-Verix-Signature`) and replay attack prevention.

---

## Self-Hosting Guide

Verix is architected for zero-vendor-lockin self-hosting on any Linux, macOS, or Windows host running Docker or bare metal.

### Production Environment Variables

Configure these variables in your `.env` file:

```ini
# Core Environment
ENVIRONMENT=production
PORT=8000
DEBUG=false

# Database Configuration (PostgreSQL recommended for production)
DATABASE_URL=postgresql+asyncpg://verix_user:verix_password@127.0.0.1:5432/verix

# Cryptographic & Security Secrets (Generate using: python -c "import secrets; print(secrets.token_urlsafe(32))")
ADMIN_API_KEY=your_secure_admin_api_key_here
MEDIA_SIGNING_KEY=your_secure_media_signing_key_here
ALLOWED_ORIGINS=["*"]

# SerpApi Intelligence Credentials
SERPAPI_API_KEY=your_serpapi_api_key_here
ENABLE_MULTI_ENGINE=true
SERPAPI_COUNTRY=in
SERPAPI_LANGUAGE=en

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

---

### Method 1: Docker Compose (Recommended)

The quickest method to deploy a production-grade stack including the Verix unified engine and an isolated PostgreSQL database.

```bash
# 1. Clone repository
git clone https://github.com/Pranjulchaurasiya/Verix.git
cd Verix

# 2. Populate environment secrets
cp .env.example .env
# Edit .env and insert your SERPAPI_API_KEY and generated keys

# 3. Launch the container stack
docker compose up -d --build
```

The stack will start:
- **Verix Authenticity Engine + UI Console**: `http://localhost:8000`
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **PostgreSQL 16 Engine**: Isolated on internal Docker network

View container logs:
```bash
docker compose logs -f verix-app
```

---

### Method 2: Standalone Docker Container

If using an external managed PostgreSQL instance (AWS RDS, Neon, Supabase, or local Postgres):

```bash
# 1. Build the multi-stage image
docker build -t verix-engine:latest .

# 2. Run container
docker run -d \
  --name verix-engine \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL="postgresql+asyncpg://user:password@db-host:5432/verix" \
  -e SERPAPI_API_KEY="your_serpapi_key" \
  -e MEDIA_SIGNING_KEY="your_media_signing_key" \
  -e ADMIN_API_KEY="your_admin_api_key" \
  -e ALLOWED_ORIGINS='["*"]' \
  -v verix_uploads:/app/uploads \
  --restart unless-stopped \
  verix-engine:latest
```

---

### Method 3: Bare Metal / Systemd (Linux / VPS)

#### 1. System Requirements & Dependencies
- Python 3.11, 3.12, or 3.13
- Node.js 20+ and `pnpm`
- PostgreSQL 14+

```bash
# Install Python virtual environment & backend packages
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Build static Next.js frontend into frontend/out
cd frontend
pnpm install
pnpm build
cd ..
```

#### 2. Create Systemd Service (`/etc/systemd/system/verix.service`)
```ini
[Unit]
Description=Verix Visual Intelligence Engine
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/verix
EnvironmentFile=/opt/verix/.env
ExecStart=/opt/verix/.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now verix
sudo systemctl status verix
```

---

### Method 4: Production Nginx Reverse Proxy with SSL

Configure Nginx as a reverse proxy for custom domains and automatic Let's Encrypt SSL:

```nginx
server {
    server_name verix.yourdomain.com;

    client_max_body_size 25M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable SSL via Certbot:
```bash
sudo certbot --nginx -d verix.yourdomain.com
```

---

## Automated Testing & Ground-Truth Benchmarks

### 1. Pytest Test Suite (60 Automated Tests)
```bash
python -m pytest backend/tests -v
```
- **100% Pass Rate (60/60 passed in 2.15s)** covering API endpoints, SSRF rejection, Merkle tree math, Ed25519 signatures, rate limiting, and webhooks.

### 2. Ground-Truth Invariant Benchmark Harness
```bash
python evaluate_ground_truth.py
```
- Automatically executes 7 subsystem checks in **19.28ms** mean latency, generating [`benchmark_report.json`](file:///c:/Users/pranj/Documents/Verix/benchmark_report.json) and [`BENCHMARK_REPORT.md`](file:///c:/Users/pranj/Documents/Verix/BENCHMARK_REPORT.md).

### 3. Standalone Cryptographic CLI Verification
```bash
# Download any audit dossier from the UI or API and verify it offline:
python verify_evidence_cli.py path/to/dossier.json --verbose
```
```text
[*] Checking file: dossier.json
[*] Signature check (Ed25519): PASS
[*] Merkle Tree Root: 7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
[*] Verifying inclusion proofs: 5/5 PASSED
==================================================
RESULT: VERIFIED (Tamper-evident authenticity confirmed)
==================================================
```

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/analyze` | Submit image upload or marketplace URL for authenticity investigation |
| `GET` | `/api/v1/scans/{id}` | Retrieve persistent scan record and visual evidence |
| `GET` | `/api/v1/scans/{id}/export` | Export Verix Verifiable Dossier (VVD) in JSON or CSV format |
| `GET` | `/api/v1/audit/keys` | Retrieve active RFC 8032 Ed25519 public keys |
| `GET` | `/api/v1/audit/dossier/{id}` | Retrieve signed Merkle audit dossier with inclusion proofs |
| `POST` | `/api/v1/audit/verify` | Verify digital signature and arbitrary leaf Merkle inclusion proof |
| `POST` | `/api/v1/enforce/takedown` | Generate statutory DMCA/VeRO takedown notice package |
| `GET` | `/api/v1/admin/health` | Comprehensive infrastructure and API health telemetry |
| `GET` | `/api/v1/admin/stats` | Operational metrics (average trust scores, cache hit rates) |

---

## Repository Structure

```text
verix/
├── .github/workflows/ci.yml       # Automated GitHub Actions CI/CD pipeline
├── backend/                       # FastAPI core service
│   ├── app/
│   │   ├── api/v1/                # REST endpoints (analyze, scans, audit, enforce)
│   │   ├── models/                # SQLAlchemy database models
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── services/              # Core business & crypto logic
│   │   │   ├── audit_merkle.py    # RFC 8032 Ed25519 & Merkle tree proofs
│   │   │   ├── serpapi.py         # SerpApi Google Lens client & caching
│   │   │   ├── scraper.py         # SSRF-protected product image extractor
│   │   │   ├── pricing.py         # Pricing dispersion & counterfeit fence detector
│   │   │   ├── provenance.py      # C2PA & synthetic AI generator detector
│   │   │   ├── takedown.py        # Statutory DMCA/VeRO notice compiler
│   │   │   └── sanitizer.py       # Non-accusatory language guardrails
│   │   └── main.py                # ASGI application entrypoint
│   ├── requirements.txt           # Production Python dependencies
│   └── tests/                     # 61 automated pytest tests
├── frontend/                      # Next.js 16 (Turbopack) frontend console
│   ├── app/                       # Next.js App Router (pages & layouts)
│   ├── components/                # React components (form, matches, pricing, dossier)
│   └── lib/                       # Types, client helpers, and verdict metadata
├── docs/                          # Architecture guides & UI visual assets
│   └── images/                    # UI screenshots (console, history, system)
├── evaluate_ground_truth.py       # Automated benchmark harness
├── verify_evidence_cli.py         # Standalone offline CLI verifier
├── docker-compose.yml             # Self-hosting Docker Compose orchestration
├── Dockerfile                     # Multi-stage production container
├── render.yaml                    # Render Blueprint deployment configuration
├── .env.example                   # Annotated environment variable template
├── Makefile                       # Developer command runner
├── pyproject.toml                 # Modern Python packaging & tool configuration
├── SECURITY.md                    # Responsible disclosure & security architecture
├── CONTRIBUTING.md                # Contribution guidelines
└── LICENSE                        # MIT License
```

---

## Frequently Asked Questions (FAQ)

<details>
<summary><b>1. Why does Verix use deterministic mathematical scoring instead of an LLM?</b></summary>
<br/>

Large Language Models (LLMs) are prone to non-deterministic outputs and hallucinations, which are unacceptable when evaluating potential fraud or legal IP disputes. Verix uses **100% deterministic mathematical boundaries** (statistical IQR pricing fences, distinct domain counts, and perceptual image hashing) to ensure that the exact same evidence always yields the exact same auditable score.
</details>

<details>
<summary><b>2. What makes the Verix evidence dossier tamper-evident?</b></summary>
<br/>

Every harvested match, timestamp, and price point is canonicalized under **RFC 8785 (JCS)**, hashed into a **Binary Merkle Tree**, and digitally signed using **RFC 8032 Ed25519**. Third parties can download any dossier `.json` and verify its inclusion proofs and digital signature completely offline using `verify_evidence_cli.py` without trusting or querying the Verix server.
</details>

<details>
<summary><b>3. How does Verix minimize SerpApi API costs and latency?</b></summary>
<br/>

Verix implements a multi-tier caching strategy:
- **Perceptual & Cryptographic Hash Indexing**: Images are indexed by 64-bit dHash and SHA-256, allowing instant cache hits for previously analyzed images.
- **Fail-Closed Early Exit**: If fewer than 2 distinct merchant domains are detected, the system safely exits without triggering secondary deep queries.
- **24-Hour Evidence TTL**: High-confidence marketplace visual matches are cached to deliver sub-millisecond responses for repeat investigations.
</details>

<details>
<summary><b>4. How does Verix protect against defamation and false accusations?</b></summary>
<br/>

Verix enforces a strict **Non-Accusatory Policy**. The engine never outputs defamatory words like *"scam"*, *"fraudster"*, or *"criminal"*. Instead, all verdicts are framed objectively based on measurable facts (e.g., *"unverified merchant domain"*, *"image appears across multiple third-party marketplaces"*, *"pricing anomaly detected: 84% below median retail"*).
</details>

<details>
<summary><b>5. How is Server-Side Request Forgery (SSRF) prevented during URL extraction?</b></summary>
<br/>

When a user submits a storefront URL, the ingestion firewall resolves the domain's IP addresses prior to making any HTTP request. It strictly rejects private IP ranges (RFC 1918), loopback addresses (127.0.0.1/::1), and cloud metadata endpoints (169.254.169.254). Redirects are independently re-validated at every hop, and responses are inspected for valid image magic bytes.
</details>

---

## License

Distributed under the **MIT License**. See [`LICENSE`](file:///c:/Users/pranj/Documents/Verix/LICENSE) for more information.
