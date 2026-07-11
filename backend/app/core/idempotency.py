import hashlib
import json
import uuid

from app.core.redis import redis_client
from app.core.redis_keys import tenant_key


class IdempotencyService:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds

    def build_key(self, tenant_id: uuid.UUID, operation: str, payload: dict) -> str:
        body = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        return tenant_key(tenant_id, "idem", operation, digest)

    async def acquire(self, tenant_id: uuid.UUID, operation: str, payload: dict) -> bool:
        key = self.build_key(tenant_id, operation, payload)
        try:
            return bool(await redis_client.set(key, "1", ex=self.ttl_seconds, nx=True))
        except Exception:
            # fail-open for availability
            return True
