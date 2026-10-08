.PHONY: all install test benchmark typecheck build dev-backend dev-frontend clean help

help:
	@echo "Verix — Developer Commands"
	@echo "=================================================="
	@echo "  make install       Install backend and frontend dependencies"
	@echo "  make test          Run full backend pytest test suite"
	@echo "  make benchmark     Run ground-truth benchmark harness"
	@echo "  make typecheck     Run TypeScript compiler and Python syntax check"
	@echo "  make build         Build Next.js static production bundle"
	@echo "  make dev-backend   Start FastAPI development server on port 8000"
	@echo "  make dev-frontend  Start Next.js development server on port 3000"
	@echo "  make clean         Remove build artifacts and cache directories"

install:
	python -m pip install -r backend/requirements.txt
	cd fake-check-ai-development && pnpm install

test:
	python -m pytest backend/tests -v

benchmark:
	python evaluate_ground_truth.py

typecheck:
	cd fake-check-ai-development && pnpm exec tsc --noEmit
	python -m compileall backend

build:
	cd fake-check-ai-development && pnpm build

dev-backend:
	python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

dev-frontend:
	cd fake-check-ai-development && pnpm dev

clean:
	python -c "import shutil, os; [shutil.rmtree(p) for p in ['.pytest_cache', '.uv-cache', '.deepeval', 'fake-check-ai-development/.next', 'fake-check-ai-development/out'] if os.path.exists(p)]"
	python -c "import os, glob; [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True)]"
