"""Scan record database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, JSON
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ScanRecord(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_hash = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    
    # Context & Input
    persona_mode = Column(String(20), nullable=False, default="buyer")  # "buyer" or "seller"
    input_type = Column(String(20), nullable=False, default="upload")    # "upload" or "url"
    source_url = Column(String(2048), nullable=True)
    image_url = Column(String(2048), nullable=False)
    product_availability = Column(String(30), nullable=True, default="unknown")
    # Hash of the client-provided anonymous session identifier. This scopes
    # history without storing a raw browser identifier.
    client_scope_hash = Column(String(64), nullable=True, index=True)
    
    # Processing Status
    status = Column(String(30), nullable=False, default="completed")  
    # statuses: "completed", "trusted_whitelist", "insufficient_data", "stale_cached", "failed"
    
    # Risk Intelligence Verdict
    trust_score = Column(Integer, nullable=True)  # 0-100; None for insufficient data
    confidence = Column(String(20), nullable=True)  # "low", "medium", "high"
    explanation = Column(Text, nullable=False)
    matched_domains = Column(JSON, nullable=False, default=list)
    
    # Audit & Flags
    is_whitelist_bypass = Column(Boolean, default=False, nullable=False)
    is_stale = Column(Boolean, default=False, nullable=False)
    stale_original_timestamp = Column(DateTime(timezone=True), nullable=True)
    raw_serpapi_response = Column(JSON, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "image_hash": self.image_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "persona_mode": self.persona_mode,
            "input_type": self.input_type,
            "source_url": self.source_url,
            "image_url": self.image_url,
            "product_availability": self.product_availability,
            "status": self.status,
            "trust_score": self.trust_score,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "matched_domains": self.matched_domains,
            "is_whitelist_bypass": self.is_whitelist_bypass,
            "is_stale": self.is_stale,
            "stale_original_timestamp": self.stale_original_timestamp.isoformat() if self.stale_original_timestamp else None
        }
