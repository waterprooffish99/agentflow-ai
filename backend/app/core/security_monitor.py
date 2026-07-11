import uuid

import structlog

from app.core.redis import redis_client
from app.core.redis_keys import tenant_key

logger = structlog.get_logger()


async def record_auth_failure(identifier: str) -> None:
    try:
        key = tenant_key("global", "security", "auth_fail", identifier)
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 3600)
        if count >= 10:
            logger.warning("suspicious_auth_failures", identifier=identifier, count=count)
    except Exception:
        return


async def trace_admin_operation(tenant_id: uuid.UUID | None, operation: str, actor_id: uuid.UUID | None) -> None:
    logger.info(
        "admin_operation",
        tenant_id=str(tenant_id) if tenant_id else None,
        operation=operation,
        actor_id=str(actor_id) if actor_id else None,
    )
