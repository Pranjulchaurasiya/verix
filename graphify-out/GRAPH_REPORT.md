# Graph Report - Verix  (2026-10-08)

## Corpus Check
- 104 files · ~218,905 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 747 nodes · 1340 edges · 49 communities (36 shown, 7 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- result-view.tsx
- check-form.tsx
- package.json
- analyze_product
- analyze_image_provenance
- Verix — Cryptographically-Anchored Visual Intelligence & Counterfeit Risk Mitigation Engine
- authenticity_verification_utility/DESIGN.md
- history-view.tsx
- compilerOptions
- test_security.py
- TelemetryTracker
- components.json
- ScanRecord
- precision_ledger_verification_console/DESIGN.md
- dependencies
- evaluate_ground_truth.py
- test_insufficient_data.py
- check-scan-contract.cjs
- v1/webhooks.py
- v1/admin.py
- scans.py
- Contributing to Verix
- Obsidian — High-Contrast Dark
- next.config.mjs
- postcss.config.mjs
- app/__init__.py
- verify_live.py
- init_db
- analyze.py
- site-header.tsx
- Security Policy
- verix
- INTEGRATION.md
- next-env.d.ts
- storage.py
- Verix — SerpApi Hackathon 2026 Master Showcase & Technical Defense Dossier
- check-experience.tsx
- main.py
- react
- layout.tsx
- Verix Invariant & Ground-Truth Benchmark Report
- devDependencies
- scripts

## God Nodes (most connected - your core abstractions)
1. `ScanRecord` - 25 edges
2. `analyze_product()` - 24 edges
3. `MerkleTree` - 19 edges
4. `lucide-react` - 18 edges
5. `init_db()` - 17 edges
6. `react` - 17 edges
7. `sign_audit_manifest()` - 16 edges
8. `is_domain_whitelisted()` - 16 edges
9. `compilerOptions` - 16 edges
10. `search_google_lens()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `run_benchmark_suite()` --calls--> `analyze_price_distribution()`  [EXTRACTED]
  evaluate_ground_truth.py → backend/app/services/pricing.py
- `run_benchmark_suite()` --calls--> `analyze_image_provenance()`  [EXTRACTED]
  evaluate_ground_truth.py → backend/app/services/provenance.py
- `run_benchmark_suite()` --calls--> `compute_signature()`  [EXTRACTED]
  evaluate_ground_truth.py → backend/app/services/webhooks.py
- `run_benchmark_suite()` --calls--> `verify_signature()`  [EXTRACTED]
  evaluate_ground_truth.py → backend/app/services/webhooks.py
- `run_benchmark_suite()` --calls--> `is_domain_whitelisted()`  [EXTRACTED]
  evaluate_ground_truth.py → backend/app/services/whitelist.py

## Import Cycles
- None detected.

## Communities (49 total, 7 thin omitted)

### Community 0 - "result-view.tsx"
Cohesion: 0.17
Nodes (14): DossierDialog(), DossierDialogProps, EvidencePanel(), MatchList(), MerkleVerifyBadge(), MerkleVerifyBadgeProps, PricingDistributionCard(), PricingDistributionCardProps (+6 more)

### Community 1 - "check-form.tsx"
Cohesion: 0.18
Nodes (11): EXAMPLES, Badge(), badgeVariants, Input(), Tabs(), TabsContent(), TabsList(), tabsListVariants (+3 more)

### Community 2 - "package.json"
Cohesion: 0.11
Nodes (18): name, packageManager, private, version, @base-ui/react, clsx, geist, postcss (+10 more)

### Community 3 - "analyze_product"
Cohesion: 0.09
Nodes (38): analyze_product(), AsyncSession, post, Public-image evidence assessment endpoint. Accepts either an uploaded product…, Cleans untrusted scraped text (e.g. product titles, snippets) before sending to…, sanitize_scraped_text(), canonicalize_evidence_url(), _dedupe_matches() (+30 more)

### Community 4 - "analyze_image_provenance"
Cohesion: 0.13
Nodes (21): analyze_price_distribution(), normalize_to_usd(), parse_price_and_currency(), Any, Multi-Retailer Pricing Anomaly & Outlier Distribution Engine. Performs robust…, Extracts numeric float and standardized currency symbol., Converts price to USD using benchmark FX table., Computes interquartile range (IQR), median, and modified Z-scores across all… (+13 more)

### Community 5 - "Verix — Cryptographically-Anchored Visual Intelligence & Counterfeit Risk Mitigation Engine"
Cohesion: 0.13
Nodes (14): 1. Clone & Configure, 1. Pytest Test Suite (54 Automated Tests), 2. Ground-Truth Invariant Benchmark Harness, 2. Install Dependencies, 3. Launch Development Servers, 3. Standalone Cryptographic CLI Verification, 🧪 Automated Testing & Ground-Truth Benchmarks, ✨ Key Capabilities (+6 more)

### Community 6 - "authenticity_verification_utility/DESIGN.md"
Cohesion: 0.09
Nodes (21): Brand & Style, Breakpoints & Reflow Rules, Buttons, Cards & Evidence Panels, Colors, Components, Core Roles, Elevation & Depth (+13 more)

### Community 7 - "history-view.tsx"
Cohesion: 0.21
Nodes (6): Dialog(), DialogContent(), DialogHeader(), DialogTitle(), DialogTrigger(), VerdictBadge()

### Community 8 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 9 - "test_security.py"
Cohesion: 0.10
Nodes (25): Require an admin secret in production; allow local development probes., require_admin_key(), check_rate_limit(), FastAPI dependency to enforce rate limits per client IP., SlidingWindowRateLimiter, extract_product_image_from_url(), _get_limited(), _is_tracking_or_icon_url() (+17 more)

### Community 10 - "TelemetryTracker"
Cohesion: 0.12
Nodes (3): Any, Telemetry and operational metrics tracker for Verix., TelemetryTracker

### Community 11 - "components.json"
Cohesion: 0.11
Nodes (17): aliases, components, hooks, lib, ui, utils, iconLibrary, rsc (+9 more)

### Community 12 - "ScanRecord"
Cohesion: 0.14
Nodes (12): create_takedown_notice(), get_takedown_notice_by_scan_id(), AsyncSession, BaseModel, get, post, Generates a formal, cryptographically anchored DMCA / VeRO takedown notice…, Convenience endpoint to retrieve an automated takedown package for a scan. (+4 more)

### Community 13 - "precision_ledger_verification_console/DESIGN.md"
Cohesion: 0.12
Nodes (16): Brand & Style, Buttons, Chromatic Strategy, Colors, Components, Diagrammatic Data Cards, Elevation & Depth, Inputs & Verification Fields (+8 more)

### Community 14 - "dependencies"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, class-variance-authority, clsx, cn, geist, lucide-react, next (+8 more)

### Community 15 - "evaluate_ground_truth.py"
Cohesion: 0.06
Nodes (58): get_anchored_dossier(), get_audit_public_keys(), AsyncSession, BaseModel, get, post, Audit and Cryptographic Verification Endpoints. Allows third-party judges,…, Verifies an audit dossier's Ed25519 digital signature and optional Merkle… (+50 more)

### Community 16 - "test_insufficient_data.py"
Cohesion: 0.09
Nodes (33): _has_sufficient_evidence(), Require multiple matches from distinct domains before scoring., evaluate_authenticity_heuristic(), evaluate_authenticity_with_groq(), evaluate_with_gemini(), GeminiFlaggedDomain, GeminiVerdictSchema, is_valid_api_key() (+25 more)

### Community 17 - "check-scan-contract.cjs"
Cohesion: 0.17
Nodes (11): {analyzeImage}, assert, demo, fs, mapped, {mapScanResponse}, payload, raw (+3 more)

### Community 18 - "v1/webhooks.py"
Cohesion: 0.06
Nodes (53): create_webhook_subscription(), delete_webhook_subscription(), get_dispatched_webhook_events(), get_webhook_subscriptions(), BaseModel, delete, get, post (+45 more)

### Community 20 - "v1/admin.py"
Cohesion: 0.24
Nodes (11): get_system_health(), get_system_stats(), AsyncSession, get, Decoupled Admin and System Ops Health endpoints., Decoupled health probe for system monitoring and ops dashboards. Stays…, Operational statistics, bypass counts, and scan risk distribution., AdminHealthResponse (+3 more)

### Community 21 - "scans.py"
Cohesion: 0.19
Nodes (16): delete_scan(), export_scan_audit_report(), get_scan_by_id(), list_recent_scans(), AsyncSession, delete, get, Scan retrieval and history endpoints. (+8 more)

### Community 22 - "Contributing to Verix"
Cohesion: 0.22
Nodes (8): Code of Conduct, Contributing to Verix, Contribution Principles & Policies, Development Workflow, Initial Setup, Prerequisites, Running the Test Suite, Submitting Pull Requests

### Community 23 - "Obsidian — High-Contrast Dark"
Cohesion: 0.25
Nodes (7): Colors, Components, Elevation, North Star: "Precision in Darkness", Obsidian — High-Contrast Dark, Rules, Typography

### Community 33 - "init_db"
Cohesion: 0.10
Nodes (33): AsyncClient, _annotate_source_legitimacy(), Attach explainable source signals; this assesses the source, not authenticity., init_db(), Initializes tables on startup., detect_screenshot_and_extract_metadata(), parse_price_str(), Any (+25 more)

### Community 34 - "analyze.py"
Cohesion: 0.29
Nodes (15): analyze_batch(), _process_batch_item(), Main scan and authenticity analysis API endpoint., Concurrent multi-image/multi-product batch analysis endpoint. Processes up to…, AnalyzeRequestUrl, BatchItemRequest, BatchItemResult, BatchScanRequest (+7 more)

### Community 35 - "site-header.tsx"
Cohesion: 0.15
Nodes (6): EVENT_TONE, SystemPage(), HistoryView(), NAV, SiteHeader(), WebhookTester()

### Community 36 - "Security Policy"
Cohesion: 0.40
Nodes (4): Reporting a Vulnerability, Security Architecture & Defenses, Security Policy, Supported Versions

### Community 40 - "storage.py"
Cohesion: 0.17
Nodes (14): compute_image_hashes(), _media_key(), Image storage, perceptual hashing, and URL management., Return a short-lived bearer link for a locally stored scan image., Computes both exact SHA256 and perceptual average hash (aHash). Returns…, Saves image bytes to the uploads directory. Returns (saved_filepath,…, save_uploaded_image(), signed_image_url() (+6 more)

### Community 41 - "Verix — SerpApi Hackathon 2026 Master Showcase & Technical Defense Dossier"
Cohesion: 0.15
Nodes (12): 1. Complete 10-Sprint Engineering Progression, 2. 7-Point Benchmark Evaluation Harness (`evaluate_ground_truth.py`), 3. The 90-Second Hackathon Judge Pitch & Live Demo Walkthrough, 4. Architecture Diagram, 5. Security & Invariant Guarantees, Act 1: The Problem (0:00 - 0:20), Act 2: SerpApi Ingestion + Threat Triangulation (0:20 - 0:50), Act 3: Cryptographic Integrity & Offline Verification (0:50 - 1:15) (+4 more)

### Community 42 - "check-experience.tsx"
Cohesion: 0.16
Nodes (11): BatchResultView(), CheckExperience(), HEADINGS, Phase, CheckForm(), SubmitPayload, OPTIONS, PersonaToggle() (+3 more)

### Community 44 - "main.py"
Cohesion: 0.14
Nodes (15): Seller Asset Protection & Enforcement API endpoints., Application configuration using Pydantic Settings., Settings, get_db(), Database engine, declarative base, and session generator., FastAPI dependency for obtaining an async database session., lifespan(), AsyncSession (+7 more)

### Community 45 - "react"
Cohesion: 0.29
Nodes (4): ResultSkeleton(), STAGES, Skeleton(), react

### Community 46 - "layout.tsx"
Cohesion: 0.25
Nodes (6): metadata, viewport, Toaster(), next, next-themes, sonner

### Community 47 - "Verix Invariant & Ground-Truth Benchmark Report"
Cohesion: 0.50
Nodes (3): Benchmark Scenario Matrix, Subsystem Invariant Summary, Verix Invariant & Ground-Truth Benchmark Report

### Community 48 - "devDependencies"
Cohesion: 0.25
Nodes (8): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, typescript

### Community 49 - "scripts"
Cohesion: 0.50
Nodes (4): scripts, build, dev, start

## Knowledge Gaps
- **166 isolated node(s):** `metadata`, `viewport`, `EVENT_TONE`, `$schema`, `style` (+161 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 376 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanRecord` connect `ScanRecord` to `init_db`, `analyze.py`, `analyze_product`, `storage.py`, `main.py`, `evaluate_ground_truth.py`, `v1/admin.py`, `scans.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `is_domain_whitelisted()` connect `init_db` to `test_insufficient_data.py`, `analyze.py`, `analyze_product`, `evaluate_ground_truth.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ScanRecord` (e.g. with `get_system_stats()` and `analyze_product()`) actually correct?**
  _`ScanRecord` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `analyze_product()` (e.g. with `ScanRecord` and `MatchedDomainItem`) actually correct?**
  _`analyze_product()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `MerkleTree` (e.g. with `get_anchored_dossier()` and `verify_audit_dossier()`) actually correct?**
  _`MerkleTree` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `metadata`, `viewport`, `EVENT_TONE` to the rest of the system?**
  _166 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._