"""Pydantic schemas for Scan requests and responses."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

PersonaMode = Literal["buyer", "seller"]
ScanStatus = Literal["completed", "trusted_whitelist", "insufficient_data", "stale_cached", "failed"]
ConfidenceLevel = Literal["low", "medium", "high"]
RiskCategory = Literal["trusted", "low_risk", "moderate_risk", "high_risk", "insufficient_data"]

class AnalyzeRequestUrl(BaseModel):
    url: str = Field(..., description="E-commerce listing URL or direct image URL to analyze")
    persona_mode: PersonaMode = Field(default="buyer", description="Either 'buyer' or 'seller'")

class MatchedDomainItem(BaseModel):
    domain: str
    title: Optional[str] = None
    price: Optional[str] = None
    extracted_price: Optional[float] = None
    currency: Optional[str] = None
    link: Optional[str] = None
    source: Optional[str] = None
    thumbnail: Optional[str] = None
    flagged: bool = False
    risk_note: Optional[str] = None
    is_whitelisted: bool = False
    engine: Optional[str] = None
    evidence_type: Optional[str] = None
    engines: List[str] = []
    evidence_types: List[str] = []
    corroboration_count: int = Field(1, ge=1)
    observed_at: Optional[str] = None
    legitimacy_label: Optional[str] = None
    legitimacy_score: Optional[int] = Field(None, ge=0, le=100)
    legitimacy_reasons: List[str] = []
    source_icon: Optional[str] = None
    in_stock: Optional[bool] = None

class ScanResponse(BaseModel):
    id: str
    image_hash: str
    created_at: str
    persona_mode: PersonaMode
    input_type: Literal["upload", "url"]
    source_url: Optional[str] = None
    image_url: str
    status: ScanStatus
    trust_score: Optional[int] = Field(None, ge=0, le=100, description="Web-evidence risk score (0-100), not physical product authentication; null if insufficient data")
    confidence: Optional[ConfidenceLevel] = None
    explanation: str
    matched_domains: List[MatchedDomainItem] = []
    is_whitelist_bypass: bool = False
    is_stale: bool = False
    stale_original_timestamp: Optional[str] = None
    risk_category: RiskCategory
    action_recommendation: str
    product_availability: Optional[str] = None
    provenance: Optional[str] = None
    ai_overview: Optional[str] = None
    typical_price_range: Optional[str] = None
    is_synthetic: Optional[bool] = False
    synthid_detected: Optional[bool] = False
    provenance_summary: Optional[str] = None
    detected_generators: List[str] = []
    pricing_analysis: Optional[dict] = None
    provenance_details: Optional[dict] = None
    domain_reputation: Optional[dict] = None
    comparison_videos: Optional[List[dict]] = []

class ScanListItem(BaseModel):
    id: str
    created_at: str
    persona_mode: PersonaMode
    input_type: str
    image_url: str
    status: str
    trust_score: Optional[int] = None
    confidence: Optional[str] = None
    risk_category: str
    match_count: int

class ScanListResponse(BaseModel):
    total: int
    items: List[ScanListItem]

class BatchItemRequest(BaseModel):
    url: str = Field(..., description="E-commerce listing URL or product image URL")
    label: Optional[str] = Field(None, description="Optional label, e.g. 'Front Photo', 'Packaging', 'Variant A'")

class BatchScanRequest(BaseModel):
    persona_mode: PersonaMode = Field(default="buyer", description="Either 'buyer' or 'seller'")
    items: List[BatchItemRequest] = Field(..., max_length=10, description="List of 1 to 10 product items/photos to scan concurrently")
    prefer_cache: bool = Field(default=True, description="Whether to reuse verified cache entries")

class BatchItemResult(BaseModel):
    url: str
    label: Optional[str] = None
    status: ScanStatus
    trust_score: Optional[int] = None
    confidence: Optional[ConfidenceLevel] = None
    risk_category: RiskCategory
    matched_domains_count: int = 0
    top_matches: List[MatchedDomainItem] = []
    explanation: str
    cache_hit: bool = False
    ai_overview: Optional[str] = None
    is_synthetic: Optional[bool] = False
    provenance_summary: Optional[str] = None
    detected_generators: List[str] = []
    pricing_analysis: Optional[dict] = None

class BatchScanResponse(BaseModel):
    batch_id: str
    created_at: str
    total_items: int
    persona_mode: PersonaMode
    aggregate_trust_score: Optional[int] = None
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    items: List[BatchItemResult]
    audit_signature: str

