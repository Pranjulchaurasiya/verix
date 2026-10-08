# Graph Report - Verix  (2026-10-08)

## Corpus Check
- 110 files · ~221,631 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 793 nodes · 1549 edges · 48 communities (38 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 47 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- result-view.tsx
- cn
- package.json
- serpapi.py
- analyze_price_distribution
- Verix — Cryptographically-Anchored Visual Intelligence & Counterfeit Risk Mitigation Engine
- authenticity_verification_utility/DESIGN.md
- history-view.tsx
- compilerOptions
- test_security.py
- TelemetryTracker
- components.json
- main.py
- precision_ledger_verification_console/DESIGN.md
- dependencies
- evaluate_ground_truth.py
- test_insufficient_data.py
- mock-engine.ts
- v1/webhooks.py
- Obsidian — High-Contrast Dark
- v1/admin.py
- scans.py
- scan-service.ts
- history-store.ts
- next.config.mjs
- postcss.config.mjs
- app/__init__.py
- verify_live.py
- types.ts
- is_domain_whitelisted
- analyze.py
- site-header.tsx
- analyze_image_provenance
- INTEGRATION.md
- next-env.d.ts
- analyze_product
- Verix — SerpApi Hackathon 2026 Master Showcase & Technical Defense Dossier
- cn
- config.py
- check-experience.tsx
- layout.tsx
- Verix Invariant & Ground-Truth Benchmark Report
- devDependencies
- scripts

## God Nodes (most connected - your core abstractions)
1. `ScanRecord` - 25 edges
2. `analyze_product()` - 24 edges
3. `MerkleTree` - 19 edges
4. `cn()` - 19 edges
5. `lucide-react` - 18 edges
6. `react` - 18 edges
7. `init_db()` - 17 edges
8. `sign_audit_manifest()` - 16 edges
9. `is_domain_whitelisted()` - 16 edges
10. `compilerOptions` - 16 edges

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

## Communities (48 total, 6 thin omitted)

### Community 0 - "result-view.tsx"
Cohesion: 0.16
Nodes (16): DossierDialog(), DossierDialogProps, EvidencePanel(), MatchList(), MerkleVerifyBadge(), MerkleVerifyBadgeProps, PricingDistributionCard(), PricingDistributionCardProps (+8 more)

### Community 1 - "cn"
Cohesion: 0.06
Nodes (9): Badge(), badgeVariants, Tabs(), TabsContent(), TabsList(), tabsListVariants, TabsTrigger(), class-variance-authority (+1 more)

### Community 2 - "package.json"
Cohesion: 0.11
Nodes (18): name, packageManager, private, version, @base-ui/react, clsx, geist, postcss (+10 more)

### Community 3 - "serpapi.py"
Cohesion: 0.11
Nodes (31): Content sanitization and prompt injection defense services., Cleans untrusted scraped text (e.g. product titles, snippets) before sending to…, sanitize_scraped_text(), canonicalize_evidence_url(), _dedupe_matches(), enrich_with_secondary_engines(), _get_cache_key(), get_mock_visual_matches() (+23 more)

### Community 4 - "analyze_price_distribution"
Cohesion: 0.25
Nodes (12): analyze_price_distribution(), normalize_to_usd(), parse_price_and_currency(), Any, Multi-Retailer Pricing Anomaly & Outlier Distribution Engine. Performs robust…, Extracts numeric float and standardized currency symbol., Converts price to USD using benchmark FX table., Computes interquartile range (IQR), median, and modified Z-scores across all… (+4 more)

### Community 5 - "Verix — Cryptographically-Anchored Visual Intelligence & Counterfeit Risk Mitigation Engine"
Cohesion: 0.25
Nodes (7): Key Capabilities & Hackathon Enhancements, Local development, Search and cost controls, Security, privacy, and deployment status, Tests and build, Verix — Cryptographically-Anchored Visual Intelligence & Counterfeit Risk Mitigation Engine, What the result means

### Community 6 - "authenticity_verification_utility/DESIGN.md"
Cohesion: 0.09
Nodes (21): Brand & Style, Breakpoints & Reflow Rules, Buttons, Cards & Evidence Panels, Colors, Components, Core Roles, Elevation & Depth (+13 more)

### Community 7 - "history-view.tsx"
Cohesion: 0.21
Nodes (7): Dialog(), DialogContent(), DialogHeader(), DialogTitle(), DialogTrigger(), Input(), react

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

### Community 12 - "main.py"
Cohesion: 0.10
Nodes (24): create_takedown_notice(), get_takedown_notice_by_scan_id(), AsyncSession, BaseModel, get, post, Seller Asset Protection & Enforcement API endpoints., Generates a formal, cryptographically anchored DMCA / VeRO takedown notice… (+16 more)

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
Cohesion: 0.06
Nodes (55): AsyncClient, _has_sufficient_evidence(), Require multiple matches from distinct domains before scoring., init_db(), Initializes tables on startup., evaluate_authenticity_heuristic(), evaluate_authenticity_with_groq(), evaluate_with_gemini() (+47 more)

### Community 17 - "mock-engine.ts"
Cohesion: 0.10
Nodes (26): analyzeImage(), buildMatches(), confidenceFor(), explanationFor(), hashSeed(), median(), NEUTRAL_DOMAINS, pickScenario() (+18 more)

### Community 18 - "v1/webhooks.py"
Cohesion: 0.06
Nodes (53): create_webhook_subscription(), delete_webhook_subscription(), get_dispatched_webhook_events(), get_webhook_subscriptions(), BaseModel, delete, get, post (+45 more)

### Community 19 - "Obsidian — High-Contrast Dark"
Cohesion: 0.25
Nodes (7): Colors, Components, Elevation, North Star: "Precision in Darkness", Obsidian — High-Contrast Dark, Rules, Typography

### Community 20 - "v1/admin.py"
Cohesion: 0.24
Nodes (11): get_system_health(), get_system_stats(), AsyncSession, get, Decoupled Admin and System Ops Health endpoints., Decoupled health probe for system monitoring and ops dashboards. Stays…, Operational statistics, bypass counts, and scan risk distribution., AdminHealthResponse (+3 more)

### Community 21 - "scans.py"
Cohesion: 0.18
Nodes (21): delete_scan(), export_scan_audit_report(), get_scan_by_id(), list_recent_scans(), AsyncSession, delete, get, Scan retrieval and history endpoints. (+13 more)

### Community 22 - "scan-service.ts"
Cohesion: 0.25
Nodes (13): load(), clientScopeHeaders(), scopedApiFetch(), deleteScan(), fetchScanById(), fetchScanHistory(), mapSavedScanResponse(), mapScanResponse() (+5 more)

### Community 23 - "history-store.ts"
Cohesion: 0.24
Nodes (12): HistoryView(), cache, clearHistory(), emit(), EMPTY, listeners, persist(), read() (+4 more)

### Community 32 - "types.ts"
Cohesion: 0.18
Nodes (17): EVENT_TONE, SystemPage(), load(), ResultView(), VerdictBadge(), fetchLiveHealth(), getHealth(), HealthEvent (+9 more)

### Community 33 - "is_domain_whitelisted"
Cohesion: 0.16
Nodes (17): _annotate_source_legitimacy(), Attach explainable source signals; this assesses the source, not authenticity., detect_screenshot_and_extract_metadata(), parse_price_str(), Any, Screenshot detection and visual OCR metadata extraction service., Performs local visual OCR analysis on uploaded image to: 1. Detect if image is…, extract_domain() (+9 more)

### Community 34 - "analyze.py"
Cohesion: 0.24
Nodes (11): analyze_batch(), _process_batch_item(), Main scan and authenticity analysis API endpoint., Concurrent multi-image/multi-product batch analysis endpoint. Processes up to…, BatchItemRequest, BatchItemResult, BatchScanRequest, BatchScanResponse (+3 more)

### Community 35 - "site-header.tsx"
Cohesion: 0.31
Nodes (3): NAV, SiteHeader(), WebhookTester()

### Community 37 - "analyze_image_provenance"
Cohesion: 0.29
Nodes (9): analyze_image_provenance(), Any, Synthetic AI Generation & Provenance Metadata Analyzer. Inspects image headers,…, Extracts provenance and synthetic generator signals from image bytes. Safe-…, test_provenance_c2pa_detection(), test_provenance_clean_camera_image(), test_provenance_empty_or_corrupt(), test_provenance_pillow_png_metadata() (+1 more)

### Community 40 - "analyze_product"
Cohesion: 0.17
Nodes (14): analyze_product(), AsyncSession, post, Public-image evidence assessment endpoint. Accepts either an uploaded product…, compute_image_hashes(), _media_key(), Image storage, perceptual hashing, and URL management., Return a short-lived bearer link for a locally stored scan image. (+6 more)

### Community 41 - "Verix — SerpApi Hackathon 2026 Master Showcase & Technical Defense Dossier"
Cohesion: 0.15
Nodes (12): 1. Complete 10-Sprint Engineering Progression, 2. 7-Point Benchmark Evaluation Harness (`evaluate_ground_truth.py`), 3. The 90-Second Hackathon Judge Pitch & Live Demo Walkthrough, 4. Architecture Diagram, 5. Security & Invariant Guarantees, Act 1: The Problem (0:00 - 0:20), Act 2: SerpApi Ingestion + Threat Triangulation (0:20 - 0:50), Act 3: Cryptographic Integrity & Offline Verification (0:50 - 1:15) (+4 more)

### Community 42 - "cn"
Cohesion: 0.38
Nodes (6): BatchResultView(), OPTIONS, PersonaToggle(), TrustScoreRing(), TrustScoreRingProps, cn()

### Community 44 - "config.py"
Cohesion: 0.33
Nodes (4): Application configuration using Pydantic Settings., Settings, Sliding-window IP rate limiter to safeguard SerpApi credit budget., BaseSettings

### Community 45 - "check-experience.tsx"
Cohesion: 0.15
Nodes (14): CheckExperience(), HEADINGS, Phase, CheckForm(), EXAMPLES, SubmitPayload, ResultSkeleton(), STAGES (+6 more)

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
- **160 isolated node(s):** `metadata`, `viewport`, `EVENT_TONE`, `$schema`, `style` (+155 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 367 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanRecord` connect `main.py` to `analyze.py`, `analyze_product`, `evaluate_ground_truth.py`, `test_insufficient_data.py`, `v1/admin.py`, `scans.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `is_domain_whitelisted()` connect `is_domain_whitelisted` to `analyze_product`, `test_insufficient_data.py`, `analyze.py`, `evaluate_ground_truth.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ScanRecord` (e.g. with `get_system_stats()` and `analyze_product()`) actually correct?**
  _`ScanRecord` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `analyze_product()` (e.g. with `ScanRecord` and `MatchedDomainItem`) actually correct?**
  _`analyze_product()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `MerkleTree` (e.g. with `get_anchored_dossier()` and `verify_audit_dossier()`) actually correct?**
  _`MerkleTree` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `metadata`, `viewport`, `EVENT_TONE` to the rest of the system?**
  _160 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `cn` be split into smaller, more focused modules?**
  _Cohesion score 0.06417112299465241 - nodes in this community are weakly interconnected._