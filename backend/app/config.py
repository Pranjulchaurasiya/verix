"""Application configuration using Pydantic Settings."""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "Verix"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server & Public URL
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    PUBLIC_BASE_URL: Optional[str] = None  # If running behind Render or tunnel
    
    # Database (Postgres on Render, SQLite fallback locally)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./verix.db",
        description="Database connection URL. Defaults to local SQLite async."
    )
    
    # External APIs
    SERPAPI_API_KEY: Optional[str] = None
    SERPAPI_API_KEYS: Optional[str] = None
    # Multi-engine evidence is the default product behavior. Deployments can
    # lower SERPAPI_MAX_SECONDARY_CALLS when credit or latency budgets require it.
    ENABLE_MULTI_ENGINE: bool = True
    SERPAPI_MAX_SECONDARY_CALLS: int = 2
    SERPAPI_COUNTRY: str = "in"
    SERPAPI_LANGUAGE: str = "en"
    GROQ_API_KEY: Optional[str] = None
    GROQ_API_KEYS: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_KEYS: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.7-flash"
    ENABLE_SYNTHID_DETECTOR: bool = True
    GCP_PROJECT_ID: Optional[str] = None
    GCP_LOCATION: str = "us-central1"
    # Experimental: generated verdicts can assert facts not established by search.
    # Keep deterministic, source-limited assessment as the public default.
    ENABLE_LLM_EVALUATION: bool = False
    
    # Deprecated compatibility flag. Ordinary inputs never use synthetic search;
    # only an explicit non-production scenario can request simulation.
    ENABLE_MOCK_FALLBACK: bool = False
    ADMIN_API_KEY: Optional[str] = None
    MEDIA_SIGNING_KEY: Optional[str] = "verix-dev-media-signing-key-2026"
    AUTH_SECRET: Optional[str] = "verix-audit-secret-2026"
    
    # Enterprise Cloud KMS & Distributed Redis Caching
    USE_CLOUD_KMS: bool = False
    KMS_KEY_ID: Optional[str] = None
    KMS_REGION: str = "us-east-1"
    REDIS_URL: Optional[str] = None
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:3000"
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            if "," in v:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            return [v]
        return v
    
    # Storage
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")
    MAX_IMAGE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15MB
    MAX_IMAGE_PIXELS: int = 25_000_000
    UPLOAD_RETENTION_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 40
    TRUSTED_PROXY_IPS: List[str] = []
    
    # Trusted Platform Whitelist (Indian & Global Major Marketplaces & Flagship Brand Domains)
    WHITELISTED_DOMAINS: List[str] = [
        # Major Indian Marketplaces
        "amazon.in",
        "flipkart.com",
        "meesho.com",
        "myntra.com",
        "ajio.com",
        "nykaa.com",
        "tatacliq.com",
        "snapdeal.com",
        "reliancedigital.in",
        "croma.com",
        "jiomart.com",
        
        # Major Global Marketplaces
        "amazon.com",
        "ebay.com",
        "walmart.com",
        "etsy.com",
        "target.com",
        
        # Major Official Brand Stores
        "apple.com",
        "nike.com",
        "adidas.co.in",
        "adidas.com",
        "samsung.com",
        "sony.co.in",
        "sony.com",
        "zara.com",
        "hm.com",
        "uniqlo.com",
        "puma.com",
        "boat-lifestyle.com",
    ]
    
    # Strict prohibited words for LLM explanations (Guardrail layer)
    BANNED_WORDS: List[str] = [
        "scam",
        "scams",
        "scammer",
        "scammers",
        "fraud",
        "frauds",
        "fraudulent",
        "illegal",
        "criminal",
        "criminals",
        "con artist",
        "rip-off",
        "ripoff",
        "cheat",
        "cheating",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
