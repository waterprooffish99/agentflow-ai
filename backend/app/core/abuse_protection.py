import uuid
import datetime as dt
from typing import Optional
import structlog
from app.core.redis import redis_client
from app.core.redis_keys import tenant_key

logger = structlog.get_logger()

class AbuseProtectionService:
    def __init__(self, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id

    async def track_failed_auth(self, ip_address: str) -> None:
        """Track failed authentication attempts for an IP."""
        key = f"abuse:auth_fail:{ip_address}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 3600) # 1 hour window
            
        if count > 10:
            logger.warning("auth_abuse_detected", ip=ip_address, count=count)
            # Future: add to blocklist

    async def detect_unusual_ai_usage(self) -> bool:
        """Heuristic for unusual AI usage spikes."""
        day_key = tenant_key(self.tenant_id, "ai", "usage", dt.date.today().isoformat())
        
        # Get requests in last hour (requires more granular tracking than we have now)
        # For now, just check daily total vs threshold
        usage_raw = await redis_client.hget(day_key, "total_tokens")
        usage = int(usage_raw) if usage_raw else 0
        
        if usage > 1000000: # 1M tokens in a day is high for beta
            logger.warning("unusual_ai_usage", tenant_id=self.tenant_id, tokens=usage)
            return True
        return False

    async def track_api_abuse(self, endpoint: str, ip_address: str) -> bool:
        """Track rapid hits to sensitive endpoints."""
        key = f"abuse:api:{endpoint}:{ip_address}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 60) # 1 minute window
            
        if count > 100: # 100 hits per minute is suspicious for most things
            logger.warning("api_abuse_detected", tenant_id=self.tenant_id, ip=ip_address, endpoint=endpoint)
            return True
        return False
