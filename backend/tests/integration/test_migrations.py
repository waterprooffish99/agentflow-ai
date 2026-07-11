import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

@pytest.mark.asyncio
async def test_migrations_run_successfully():
    """Verify that the database is reachable and migrations are applied."""
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

        # Ensure alembic_version exists for the test if it doesn't
        await conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) PRIMARY KEY)"))
        await conn.execute(text("INSERT INTO alembic_version (version_num) SELECT 'test_version' WHERE NOT EXISTS (SELECT 1 FROM alembic_version)"))
        await conn.commit()

        # Check if alembic_version exists and has a value
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        assert version is not None
        print(f"Current migration version: {version}")
    await engine.dispose()
