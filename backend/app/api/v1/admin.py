"""Decoupled Admin and System Ops Health endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from backend.app.database import get_db
from backend.app.models.scan import ScanRecord
from backend.app.schemas.admin import AdminHealthResponse, AdminStatsResponse
from backend.app.utils.telemetry import telemetry
from backend.app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])

def require_admin_key(x_admin_key: str | None = Header(default=None)):
    """Require an admin secret in production; allow local development probes."""
    if settings.ENVIRONMENT.lower() in {"development", "test"} and not settings.ADMIN_API_KEY:
        return
    if not settings.ADMIN_API_KEY or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin authentication required.")

@router.get("/health", response_model=AdminHealthResponse)
async def get_system_health(db: AsyncSession = Depends(get_db), _: None = Depends(require_admin_key)):
    """
    Decoupled health probe for system monitoring and ops dashboards.
    Stays responsive even if upstream SerpApi or Groq pipelines are degraded.
    """
    db_connected = False
    try:
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    snapshot = telemetry.snapshot()
    fail_closed_active = snapshot["fail_closed_stale_served"] > 0
    serpapi_rate = snapshot["serpapi_success_rate"]
    serpapi_operational = serpapi_rate >= 50.0

    overall_status = "healthy"
    if not db_connected or not serpapi_operational or fail_closed_active:
        overall_status = "degraded"

    return AdminHealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=snapshot["uptime_seconds"],
        database_connected=db_connected,
        serpapi_configured=bool(settings.SERPAPI_API_KEY),
        groq_configured=bool(settings.GROQ_API_KEY),
        gemini_configured=bool(settings.GEMINI_API_KEY),
        llm_eval_enabled=bool(settings.ENABLE_LLM_EVALUATION),
        serpapi_operational=serpapi_operational,
        fail_closed_mode_active=fail_closed_active,
        environment=settings.ENVIRONMENT,
        version=settings.VERSION
    )

@router.get("/stats", response_model=AdminStatsResponse)
async def get_system_stats(db: AsyncSession = Depends(get_db), _: None = Depends(require_admin_key)):
    """Operational statistics, bypass counts, and scan risk distribution."""
    snapshot = telemetry.snapshot()
    
    # Query database for persistent stats
    total_q = await db.execute(select(func.count(ScanRecord.id)))
    total_db_scans = total_q.scalar() or 0
    
    wl_q = await db.execute(select(func.count(ScanRecord.id)).where(ScanRecord.is_whitelist_bypass == True))
    wl_bypasses = wl_q.scalar() or 0
    
    insufficient_q = await db.execute(select(func.count(ScanRecord.id)).where(ScanRecord.status == "insufficient_data"))
    insufficient_scans = insufficient_q.scalar() or 0
    
    stale_q = await db.execute(select(func.count(ScanRecord.id)).where(ScanRecord.is_stale == True))
    stale_scans = stale_q.scalar() or 0
    
    completed_scans = max(0, total_db_scans - wl_bypasses - insufficient_scans)
    
    # Persona counts
    buyer_q = await db.execute(select(func.count(ScanRecord.id)).where(ScanRecord.persona_mode == "buyer"))
    buyer_count = buyer_q.scalar() or 0
    seller_count = max(0, total_db_scans - buyer_count)
    
    # Risk score average
    avg_score_q = await db.execute(select(func.avg(ScanRecord.trust_score)).where(ScanRecord.trust_score != None))
    avg_score = avg_score_q.scalar()
    avg_score_float = round(float(avg_score), 1) if avg_score is not None else snapshot["average_trust_score"]
    
    # Risk distribution
    high_risk_q = await db.execute(
        select(func.count(ScanRecord.id)).where(ScanRecord.trust_score < 50, ScanRecord.trust_score != None)
    )
    high_risk = high_risk_q.scalar() or 0
    
    mod_risk_q = await db.execute(
        select(func.count(ScanRecord.id)).where(
            ScanRecord.trust_score >= 50, 
            ScanRecord.trust_score < 80, 
            ScanRecord.trust_score != None
        )
    )
    mod_risk = mod_risk_q.scalar() or 0
    
    low_risk_q = await db.execute(
        select(func.count(ScanRecord.id)).where(
            ScanRecord.trust_score >= 80, 
            ScanRecord.is_whitelist_bypass == False,
            ScanRecord.trust_score != None
        )
    )
    low_risk = low_risk_q.scalar() or 0

    return AdminStatsResponse(
        total_scans=total_db_scans,
        whitelist_bypasses=wl_bypasses,
        insufficient_data_scans=insufficient_scans,
        fail_closed_served_stale=stale_scans or snapshot["fail_closed_stale_served"],
        direct_completed_scans=completed_scans,
        average_trust_score=avg_score_float,
        serpapi_success_rate=snapshot["serpapi_success_rate"],
        serpapi_credits_saved=snapshot.get("serpapi_credits_saved", 0),
        persona_breakdown={
            "buyer": buyer_count,
            "seller": seller_count
        },
        risk_distribution={
            "trusted": wl_bypasses,
            "low_risk": low_risk,
            "moderate_risk": mod_risk,
            "high_risk": high_risk,
            "insufficient_data": insufficient_scans
        }
    )
