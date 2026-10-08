"""Seller Asset Protection & Enforcement API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.scan import ScanRecord
from backend.app.services.takedown import generate_takedown_package

router = APIRouter(prefix="/enforce", tags=["enforce"])


class TakedownRequest(BaseModel):
    scan_id: str = Field(..., description="Scan ID corresponding to the protected asset")
    claimant_name: Optional[str] = Field(None, description="Name of the brand or catalog copyright owner")
    product_title: Optional[str] = Field(None, description="Title/description of the original product photography")
    original_work_url: Optional[str] = Field(None, description="URL of the authentic catalog listing")


@router.post("/takedown")
async def create_takedown_notice(
    payload: TakedownRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a formal, cryptographically anchored DMCA / VeRO takedown notice package
    for unauthorized listings detected by SerpApi Google Lens.
    """
    stmt = select(ScanRecord).where(ScanRecord.id == payload.scan_id)
    res = await db.execute(stmt)
    scan = res.scalars().first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found for takedown package generation."
        )

    matched = scan.matched_domains or []
    pkg = generate_takedown_package(
        scan_id=scan.id,
        image_hash=scan.image_hash,
        matched_domains=matched,
        claimant_name=payload.claimant_name,
        product_title=payload.product_title,
        original_work_url=payload.original_work_url or scan.source_url
    )
    return pkg


@router.get("/takedown/{scan_id}")
async def get_takedown_notice_by_scan_id(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Convenience endpoint to retrieve an automated takedown package for a scan."""
    stmt = select(ScanRecord).where(ScanRecord.id == scan_id)
    res = await db.execute(stmt)
    scan = res.scalars().first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found."
        )

    matched = scan.matched_domains or []
    pkg = generate_takedown_package(
        scan_id=scan.id,
        image_hash=scan.image_hash,
        matched_domains=matched,
        original_work_url=scan.source_url
    )
    return pkg
