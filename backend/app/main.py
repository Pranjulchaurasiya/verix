"""Main FastAPI entrypoint for Verix Authenticity Intelligence."""

import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.api.v1.analyze import router as analyze_router
from backend.app.api.v1.scans import router as scans_router
from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.audit import router as audit_router
from backend.app.api.v1.enforce import router as enforce_router
from backend.app.api.v1.webhooks import router as webhooks_router
from backend.app.database import get_db
from backend.app.models.scan import ScanRecord
from backend.app.services.storage import verify_image_signature
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from urllib.parse import urlparse
from backend.app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    if settings.ENVIRONMENT.lower() == "production" and not settings.MEDIA_SIGNING_KEY:
        raise RuntimeError("MEDIA_SIGNING_KEY is required in production.")
    await init_db()
    # Keep transient uploaded assets from becoming an unbounded data store.
    cutoff = time.time() - (settings.UPLOAD_RETENTION_DAYS * 86400)
    if os.path.isdir(settings.UPLOAD_DIR):
        for name in os.listdir(settings.UPLOAD_DIR):
            path = os.path.join(settings.UPLOAD_DIR, name)
            try:
                if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                pass
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Product authenticity and reverse-image photo protection engine for SerpApi Hackathon 2026.",
    lifespan=lifespan
)

# CORS Middleware
cors_origins = ["*"] if settings.ENVIRONMENT.lower() == "development" else settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/uploads/{name}", include_in_schema=False)
async def serve_scan_image(
    name: str,
    scan: str = Query(...),
    expires: int = Query(...),
    signature: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    upload_root = Path(settings.UPLOAD_DIR).resolve()
    candidate = (upload_root / name).resolve()
    if candidate.parent != upload_root or not verify_image_signature(scan, name, expires, signature):
        raise HTTPException(status_code=404, detail="Image not found.")
    record = (await db.execute(select(ScanRecord).where(ScanRecord.id == scan))).scalars().first()
    if not record or Path(urlparse(record.image_url).path).name != name or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(candidate, headers={"Cache-Control": "private, max-age=300"})

# Include API v1 Routers
app.include_router(analyze_router, prefix="/api/v1")
app.include_router(scans_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(enforce_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")

# Mount the built Next.js frontend. The legacy vanilla frontend was replaced
# by fake-check-ai-development and is intentionally no longer served.
frontend_dir = os.path.join(os.getcwd(), "fake-check-ai-development", "out")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    async def serve_root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "operational",
            "docs_url": "/docs",
            "frontend": "not-built",
        }
