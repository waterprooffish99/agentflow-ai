import os
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

# Set environment variables for testing
os.environ["APP_ENV"] = "test"
os.environ.setdefault("JWT_SECRET", "123456789012345678901234567890123456")
os.environ.setdefault("PUBLIC_API_KEY", "test-key")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")

# Resolve DATABASE_URL and REDIS_URL to match the actual test database configuration
db_url = os.environ.get("DATABASE_URL")
if db_url:
    if db_url.endswith("/agentflow"):
        db_url = db_url + "_test"
        os.environ["DATABASE_URL"] = db_url
else:
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5433/agentflow_test"

redis_url = os.environ.get("REDIS_URL")
if not redis_url or "localhost:6379" in redis_url:
    os.environ["REDIS_URL"] = "redis://localhost:6380/0"

from app.main import app
from app.models.base import Base
from app.core.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a session-wide engine and initialize schema."""
    engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    """Yield a database session for each test, rolling back after."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        from app.api.deps import get_db as api_get_db
        from app.core.database import get_db as core_get_db
        from app.core.database import get_db_for_tenant
        
        async def override_get_db():
            yield session
            
        async def override_get_db_for_tenant():
            yield session
            
        app.dependency_overrides[api_get_db] = override_get_db
        app.dependency_overrides[core_get_db] = override_get_db
        app.dependency_overrides[get_db_for_tenant] = override_get_db_for_tenant
        
        yield session
        
        await session.rollback()
        app.dependency_overrides.pop(api_get_db, None)
        app.dependency_overrides.pop(core_get_db, None)
        app.dependency_overrides.pop(get_db_for_tenant, None)

@pytest_asyncio.fixture
async def client():
    """Async client for integration tests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac
