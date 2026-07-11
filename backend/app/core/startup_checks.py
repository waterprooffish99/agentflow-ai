import os

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.redis import redis_client


REQUIRED_ENV = ["DATABASE_URL", "JWT_SECRET", "REDIS_URL"]


async def run_startup_checks() -> None:
    if settings.app_env == "test":
        return
    missing = [k for k in REQUIRED_ENV if not getattr(settings, k.lower(), None)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {missing}")

    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
        # Deployment safety: detect missing migration version table.
        try:
            await conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
        except Exception as exc:
            raise RuntimeError("Migration verification failed (alembic_version missing)") from exc

    pong = await redis_client.ping()
    if not pong:
        raise RuntimeError("Redis ping failed")

    if settings.app_env == "production" and settings.app_debug:
        raise RuntimeError("APP_DEBUG must be false in production")

    if settings.app_env == "production" and not settings.stripe_webhook_secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET must be set in production")
