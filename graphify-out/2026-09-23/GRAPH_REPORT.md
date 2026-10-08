# Graph Report - Verix  (2026-09-23)

## Corpus Check
- 75 files · ~205,269 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 497 nodes · 814 edges · 26 communities (16 shown, 5 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- result-view.tsx
- history-view.tsx
- package.json
- config.py
- main.py
- 🛡️ Verix — Product Authenticity & Reverse-Image Intelligence
- authenticity_verification_utility/DESIGN.md
- check-experience.tsx
- compilerOptions
- rate_limiter.py
- TelemetryTracker
- components.json
- analyze.py
- precision_ledger_verification_console/DESIGN.md
- dependencies
- app.js
- Obsidian — High-Contrast Dark
- next.config.mjs
- postcss.config.mjs
- app/__init__.py
- verify_live.py

## God Nodes (most connected - your core abstractions)
1. `cn()` - 17 edges
2. `compilerOptions` - 16 edges
3. `analyze_product()` - 15 edges
4. `init_db()` - 14 edges
5. `TelemetryTracker` - 14 edges
6. `ScanRecord` - 13 edges
7. `cn` - 12 edges
8. `analyzeImage()` - 11 edges
9. `is_domain_whitelisted()` - 10 edges
10. `lucide-react` - 10 edges

## Surprising Connections (you probably didn't know these)
- `get_system_stats()` --uses--> `ScanRecord`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/scan.py
- `get_system_health()` --uses--> `AdminHealthResponse`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/admin.py
- `get_system_stats()` --uses--> `AdminStatsResponse`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/admin.py
- `analyze_product()` --uses--> `ScanRecord`  [INFERRED]
  backend/app/api/v1/analyze.py → backend/app/models/scan.py
- `analyze_product()` --uses--> `MatchedDomainItem`  [INFERRED]
  backend/app/api/v1/analyze.py → backend/app/schemas/scan.py

## Import Cycles
- None detected.

## Communities (26 total, 5 thin omitted)

### Community 0 - "result-view.tsx"
Cohesion: 0.13
Nodes (24): EVENT_TONE, SystemPage(), MatchList(), OPTIONS, PersonaToggle(), CONFIDENCE_LABEL, ResultView(), NAV (+16 more)

### Community 1 - "history-view.tsx"
Cohesion: 0.06
Nodes (31): EXAMPLES, HistoryView(), Badge(), badgeVariants, Button(), buttonVariants, Dialog(), DialogContent() (+23 more)

### Community 2 - "package.json"
Cohesion: 0.05
Nodes (37): metadata, viewport, Toaster(), devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node (+29 more)

### Community 3 - "config.py"
Cohesion: 0.08
Nodes (34): Application configuration using Pydantic Settings., Settings, evaluate_authenticity_heuristic(), evaluate_authenticity_with_groq(), Any, Groq LLaMA structured authenticity risk decision engine., Deterministic rule-based evaluation engine. Used when Groq key is absent or…, Sends reverse-image match evidence to Groq LLaMA for structured evaluation.… (+26 more)

### Community 4 - "main.py"
Cohesion: 0.09
Nodes (30): get_system_health(), get_system_stats(), AsyncSession, get, Decoupled Admin and System Ops Health endpoints., Decoupled health probe for system monitoring and ops dashboards. Stays…, Operational statistics, bypass counts, and scan risk distribution., init_db() (+22 more)

### Community 5 - "🛡️ Verix — Product Authenticity & Reverse-Image Intelligence"
Cohesion: 0.08
Nodes (24): 1. Clone & Setup, 1. Submit Scan / Analyze Authenticity, 1. Trusted Platform Whitelist Bypass, 2. Empty / Noise Guardrail (`< 2` matches), 2. Install Dependencies, 2. Scan History, 3. Decoupled Ops Health & Stats, 3. Environment Variables (Optional) (+16 more)

### Community 6 - "authenticity_verification_utility/DESIGN.md"
Cohesion: 0.09
Nodes (21): Brand & Style, Breakpoints & Reflow Rules, Buttons, Cards & Evidence Panels, Colors, Components, Core Roles, Elevation & Depth (+13 more)

### Community 7 - "check-experience.tsx"
Cohesion: 0.10
Nodes (27): CheckExperience(), HEADINGS, Phase, CheckForm(), SubmitPayload, ResultSkeleton(), STEPS, Skeleton() (+19 more)

### Community 8 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 9 - "rate_limiter.py"
Cohesion: 0.25
Nodes (5): check_rate_limit(), Sliding-window IP rate limiter to safeguard SerpApi credit budget., FastAPI dependency to enforce rate limits per client IP., SlidingWindowRateLimiter, Request

### Community 11 - "components.json"
Cohesion: 0.11
Nodes (17): aliases, components, hooks, lib, ui, utils, iconLibrary, rsc (+9 more)

### Community 12 - "analyze.py"
Cohesion: 0.06
Nodes (52): analyze_product(), AsyncSession, Main scan and authenticity analysis API endpoint., Main product authenticity verification endpoint. Accepts either an uploaded…, get_scan_by_id(), list_recent_scans(), AsyncSession, get (+44 more)

### Community 13 - "precision_ledger_verification_console/DESIGN.md"
Cohesion: 0.12
Nodes (16): Brand & Style, Buttons, Chromatic Strategy, Colors, Components, Diagrammatic Data Cards, Elevation & Depth, Inputs & Verification Fields (+8 more)

### Community 14 - "dependencies"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, class-variance-authority, clsx, cn, geist, lucide-react, next (+8 more)

### Community 18 - "app.js"
Cohesion: 0.27
Nodes (9): executeScan(), fetchAdminStats(), loadHistory(), populateStitchRiskCards(), renderFilteredMatches(), renderResults(), setPersona(), setupMatchFilters() (+1 more)

### Community 19 - "Obsidian — High-Contrast Dark"
Cohesion: 0.25
Nodes (7): Colors, Components, Elevation, North Star: "Precision in Darkness", Obsidian — High-Contrast Dark, Rules, Typography

## Knowledge Gaps
- **145 isolated node(s):** `metadata`, `viewport`, `EVENT_TONE`, `$schema`, `style` (+140 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 260 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cn` connect `history-view.tsx` to `package.json`, `progress.tsx`, `check-experience.tsx`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `react` connect `history-view.tsx` to `package.json`, `check-experience.tsx`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `lucide-react` connect `history-view.tsx` to `result-view.tsx`, `package.json`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `analyze_product()` (e.g. with `ScanRecord` and `MatchedDomainItem`) actually correct?**
  _`analyze_product()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `metadata`, `viewport`, `EVENT_TONE` to the rest of the system?**
  _145 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `result-view.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.13063063063063063 - nodes in this community are weakly interconnected._
- **Should `history-view.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.055191256830601096 - nodes in this community are weakly interconnected._