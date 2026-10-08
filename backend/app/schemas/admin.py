"""Admin and system operations schemas."""

from typing import Dict, Optional
from pydantic import BaseModel

class AdminHealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float
    database_connected: bool
    serpapi_configured: bool
    groq_configured: bool
    gemini_configured: bool = False
    llm_eval_enabled: bool = False
    serpapi_operational: bool
    fail_closed_mode_active: bool
    environment: str
    version: str

class AdminStatsResponse(BaseModel):
    total_scans: int
    whitelist_bypasses: int
    insufficient_data_scans: int
    fail_closed_served_stale: int
    direct_completed_scans: int
    average_trust_score: Optional[float] = None
    serpapi_success_rate: float
    serpapi_credits_saved: int = 0
    persona_breakdown: Dict[str, int]
    risk_distribution: Dict[str, int]
