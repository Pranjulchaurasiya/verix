"""Database engine, declarative base, and session generator."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.app.config import settings
import logging

logger = logging.getLogger("verix.database")

# Format database URL properly for async driver
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLite async driver prefix check
if db_url.startswith("sqlite://") and not db_url.startswith("sqlite+aiosqlite://"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

from sqlalchemy.pool import NullPool

connect_args = {}
engine_kwargs = {"future": True, "echo": False}

if "sqlite" in db_url:
    connect_args = {"check_same_thread": False, "timeout": 20}
    engine_kwargs["connect_args"] = connect_args
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(
    db_url,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """FastAPI dependency for obtaining an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initializes tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Lightweight compatibility migration for existing hackathon SQLite
        # databases. Production deployments should still use Alembic for
        # future schema evolution.
        if "sqlite" in db_url:
            columns = await conn.exec_driver_sql("PRAGMA table_info(scans)")
            names = {row[1] for row in columns.fetchall()}
            if "client_scope_hash" not in names:
                await conn.exec_driver_sql("ALTER TABLE scans ADD COLUMN client_scope_hash VARCHAR(64)")
            if "product_availability" not in names:
                await conn.exec_driver_sql("ALTER TABLE scans ADD COLUMN product_availability VARCHAR(30)")
        else:
            await conn.exec_driver_sql(
                "ALTER TABLE scans ADD COLUMN IF NOT EXISTS client_scope_hash VARCHAR(64)"
            )
            await conn.exec_driver_sql(
                "ALTER TABLE scans ADD COLUMN IF NOT EXISTS product_availability VARCHAR(30)"
            )
    logger.info("Database tables initialized successfully.")
