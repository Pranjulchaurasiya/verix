# Contributing to Verix

Thank you for your interest in contributing to Verix! We welcome community contributions, bug reports, and enhancements.

## Code of Conduct

All contributors and maintainers are expected to uphold a respectful, inclusive, and professional environment.

## Development Workflow

### Prerequisites
- Python 3.11+
- Node.js 20+ & pnpm (`corepack enable pnpm`)
- Git

### Initial Setup
```bash
# 1. Clone the repository
git clone https://github.com/your-org/verix.git
cd verix

# 2. Install backend dependencies
python -m pip install -r backend/requirements.txt

# 3. Install frontend dependencies
cd fake-check-ai-development
pnpm install
cd ..

# 4. Copy environment template
cp .env.example .env
```

### Running the Test Suite
Before opening a pull request, ensure all tests pass:

```bash
# Backend pytest suite (54 unit, integration, and security tests)
python -m pytest backend/tests -v

# Automated ground-truth benchmark suite
python evaluate_ground_truth.py

# Frontend TypeScript type checking
cd fake-check-ai-development
pnpm exec tsc --noEmit
pnpm build
cd ..
```

## Contribution Principles & Policies

1. **Deterministic Mathematical Boundary:**
   - Numerical calculations (risk scoring, price median calculation, Merkle tree construction) must remain 100% deterministic with zero LLM dependence.
   - Any LLM integration must be non-blocking, optional, and safely fallback to heuristic evaluation.

2. **Strict Non-Accusatory Language Policy:**
   - User-facing descriptions, tooltips, error messages, and API responses must never make unsubstantiated or accusatory assertions (`scam`, `fraud`, `scammer`, `fake`, `criminal`).
   - Use objective risk-based terminology: `"unverified merchant domain"`, `"image appears on multiple sites"`, `"high-risk indicator"`.

3. **Zero Test Regressions:**
   - Every pull request must maintain or increase test coverage. All existing tests in `backend/tests` must pass.

4. **Cryptographic Integrity:**
   - Changes to the Merkle tree or Ed25519 signature payload must ensure compatibility with `verify_evidence_cli.py`.

## Submitting Pull Requests

1. Create a feature branch: `git checkout -b feat/my-improvement`
2. Commit your changes with clear, descriptive messages following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add Google Shopping currency normalization`
   - `fix: handle edge case in perceptual hash comparator`
   - `test: add unit test for webhook replay attack prevention`
3. Push to your fork and submit a Pull Request targeting the `main` branch.
