"""Scan retrieval and history endpoints."""

import hashlib
import hmac
import csv
import io
import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.app.database import get_db
from backend.app.models.scan import ScanRecord
from backend.app.schemas.scan import ScanResponse, ScanListResponse, ScanListItem, MatchedDomainItem
from backend.app.config import settings
from backend.app.services.availability import append_availability_guidance
from backend.app.services.storage import signed_image_url

router = APIRouter(prefix="/scans", tags=["scans"])
logger = logging.getLogger("verix.scans")

def _scope_hash(client_id: str | None) -> str:
    return hashlib.sha256((client_id or "development-anonymous").encode()).hexdigest()

def _require_client_scope(client_id: str | None) -> str:
    # Development keeps the old anonymous behavior for local evaluation.
    from backend.app.config import settings
    if settings.ENVIRONMENT.lower() == "production" and not client_id:
        raise HTTPException(status_code=400, detail="X-Client-Id is required for private scan history.")
    return _scope_hash(client_id)

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan_by_id(scan_id: str, x_client_id: str | None = Header(default=None), db: AsyncSession = Depends(get_db)):
    """Retrieve full details of a specific past scan by ID."""
    scope_hash = _require_client_scope(x_client_id)
    stmt = select(ScanRecord).where(ScanRecord.id == scan_id, ScanRecord.client_scope_hash == scope_hash)
    res = await db.execute(stmt)
    scan = res.scalars().first()
    
    if not scan and settings.ENVIRONMENT.lower() != "production":
        # Development fallback: allow retrieval by unguessable scan UUID
        scan = (await db.execute(select(ScanRecord).where(ScanRecord.id == scan_id))).scalars().first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found."
        )

    # Determine risk category
    if scan.status == "trusted_whitelist":
        risk_cat = "trusted"
    elif scan.status == "insufficient_data":
        risk_cat = "insufficient_data"
    elif (scan.trust_score or 50) >= 80:
        risk_cat = "low_risk"
    elif (scan.trust_score or 50) >= 50:
        risk_cat = "moderate_risk"
    else:
        risk_cat = "high_risk"

    action_rec = append_availability_guidance(
        "Refer to the risk signals above before making a transaction or submitting an IP claim.",
        scan.product_availability,
    )
    
    stored_provenance = "cached" if scan.is_stale else "development_fallback" if isinstance(scan.raw_serpapi_response, dict) and "Development-only" in str(scan.raw_serpapi_response.get("note", "")) else "live_serpapi"
    return ScanResponse(
        id=scan.id,
        image_hash=scan.image_hash,
        created_at=scan.created_at.isoformat() if scan.created_at else "",
        persona_mode=scan.persona_mode,
        input_type=scan.input_type,
        source_url=scan.source_url,
        image_url=signed_image_url(scan.image_url, scan.id),
        product_availability=scan.product_availability or "unknown",
        status=scan.status,
        trust_score=scan.trust_score,
        confidence=scan.confidence,
        explanation=scan.explanation,
        matched_domains=[MatchedDomainItem(**m) for m in (scan.matched_domains or [])],
        is_whitelist_bypass=scan.is_whitelist_bypass,
        is_stale=scan.is_stale,
        stale_original_timestamp=scan.stale_original_timestamp.isoformat() if scan.stale_original_timestamp else None,
        risk_category=risk_cat,
        action_recommendation=action_rec,
        provenance=stored_provenance
    )


@router.get("/{scan_id}/export")
async def export_scan_audit_report(
    scan_id: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    x_client_id: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an auditable, verifiable evidence dossier for hackathon judging and compliance.
    Supports structured JSON (with tamper-proof HMAC verification) or standardized CSV.
    """
    scope_hash = _require_client_scope(x_client_id)
    stmt = select(ScanRecord).where(ScanRecord.id == scan_id, ScanRecord.client_scope_hash == scope_hash)
    res = await db.execute(stmt)
    scan = res.scalars().first()

    if not scan and settings.ENVIRONMENT.lower() != "production":
        # Allow export via browser window.open (which cannot attach custom X-Client-Id headers)
        scan = (await db.execute(select(ScanRecord).where(ScanRecord.id == scan_id))).scalars().first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found for export."
        )

    matched = scan.matched_domains or []

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Domain", "Title", "Price", "Extracted Price", "Currency",
            "Legitimacy Label", "Legitimacy Score", "Engines", "In Stock", "Flagged", "Risk Note", "Link"
        ])
        for m in matched:
            writer.writerow([
                m.get("domain", ""),
                m.get("title", ""),
                m.get("price", ""),
                m.get("extracted_price", ""),
                m.get("currency", ""),
                m.get("legitimacy_label", ""),
                m.get("legitimacy_score", ""),
                ",".join(m.get("engines", []) or ([m.get("engine")] if m.get("engine") else [])),
                m.get("in_stock", ""),
                m.get("flagged", False),
                m.get("risk_note", ""),
                m.get("link", "")
            ])
        csv_data = output.getvalue()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="verix_audit_{scan_id[:8]}.csv"'}
        )

    canonical_payload = f"{scan.id}:{scan.image_hash}:{scan.trust_score}:{len(matched)}"
    secret = settings.AUTH_SECRET or "verix-audit-secret"
    audit_signature = hmac.new(secret.encode(), canonical_payload.encode(), hashlib.sha256).hexdigest()

    return {
        "verix_audit_dossier_version": "1.0",
        "scan_id": scan.id,
        "image_hash_sha256": scan.image_hash,
        "verified_at": scan.created_at.isoformat() if scan.created_at else None,
        "input_type": scan.input_type,
        "source_url": scan.source_url,
        "persona_mode": scan.persona_mode,
        "status": scan.status,
        "trust_score": scan.trust_score,
        "confidence": scan.confidence,
        "explanation": scan.explanation,
        "evidence_count": len(matched),
        "evidence_chain": matched,
        "audit_verification": {
            "algorithm": "HMAC-SHA256",
            "payload_digest": canonical_payload,
            "signature": audit_signature,
            "provenance": "live_serpapi" if not scan.is_stale else "cached_fallback"
        }
    }


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: str,
    x_client_id: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Delete one scan in the caller's private scope and its stored upload."""
    scope_hash = _require_client_scope(x_client_id)
    stmt = select(ScanRecord).where(ScanRecord.id == scan_id, ScanRecord.client_scope_hash == scope_hash)
    res = await db.execute(stmt)
    scan = res.scalars().first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan record not found.")

    # Only remove files whose URL resolves to the configured upload directory.
    # External source URLs and malformed paths are never treated as deletable files.
    image_url = scan.image_url or ""
    parsed_path = urlparse(image_url).path
    upload_name = Path(parsed_path).name if parsed_path.startswith("/uploads/") else ""
    upload_root = Path(settings.UPLOAD_DIR).resolve()
    if upload_name:
        candidate = (upload_root / upload_name).resolve()
        if candidate.parent == upload_root and candidate.is_file():
            try:
                candidate.unlink()
            except OSError:
                logger.warning("Could not remove upload for deleted scan %s", scan_id, exc_info=True)

    await db.delete(scan)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("", response_model=ScanListResponse)
async def list_recent_scans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    persona_mode: str = Query(None),
    x_client_id: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db)
):
    """List recent scans for the history dashboard (anonymous, non-invasive)."""
    scope_hash = _require_client_scope(x_client_id)
    base_query = select(ScanRecord).where(ScanRecord.client_scope_hash == scope_hash)
    count_query = select(func.count(ScanRecord.id)).where(ScanRecord.client_scope_hash == scope_hash)
    
    if persona_mode in ["buyer", "seller"]:
        base_query = base_query.where(ScanRecord.persona_mode == persona_mode)
        count_query = count_query.where(ScanRecord.persona_mode == persona_mode)
        
    base_query = base_query.order_by(desc(ScanRecord.created_at)).offset(offset).limit(limit)
    
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0
    
    records_res = await db.execute(base_query)
    records = records_res.scalars().all()
    
    items = []
    for r in records:
        if r.status == "trusted_whitelist":
            risk_cat = "trusted"
        elif r.status == "insufficient_data":
            risk_cat = "insufficient_data"
        elif (r.trust_score or 50) >= 80:
            risk_cat = "low_risk"
        elif (r.trust_score or 50) >= 50:
            risk_cat = "moderate_risk"
        else:
            risk_cat = "high_risk"
            
        items.append(
            ScanListItem(
                id=r.id,
                created_at=r.created_at.isoformat() if r.created_at else "",
                persona_mode=r.persona_mode,
                input_type=r.input_type,
                image_url=signed_image_url(r.image_url, r.id),
                status=r.status,
                trust_score=r.trust_score,
                confidence=r.confidence,
                risk_category=risk_cat,
                match_count=len(r.matched_domains or [])
            )
        )
        
    return ScanListResponse(total=total, items=items)
