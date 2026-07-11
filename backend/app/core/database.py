from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine with connection pooling
engine_kwargs = {
    "echo": settings.app_debug,
    "pool_pre_ping": True,
}
if settings.app_env == "test":
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = 25
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.database_url, **engine_kwargs)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: get tenant-scoped database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_for_tenant(tenant_id: str | None = None) -> AsyncGenerator[AsyncSession, None]:
    """Dependency: get database session with optional tenant context."""
    async with async_session_maker() as session:
        # Tenant context can be set via middleware for RLS
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables (for testing or initial setup)."""
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
