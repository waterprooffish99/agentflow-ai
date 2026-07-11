import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def redis_healthcheck() -> bool:
    try:
        pong = await redis_client.ping()
        return bool(pong)
    except Exception:
        return False
