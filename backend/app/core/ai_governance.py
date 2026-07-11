import datetime as dt
import uuid
from typing import Optional

from app.core.billing import get_plan
from app.core.redis import redis_client
from app.core.redis_keys import tenant_key


class AIGovernanceService:
    def __init__(self):
        # Default fallback if tier is unknown
        self.default_daily_quota = 2000

    def _daily_key(self, tenant_id: uuid.UUID, day: dt.date) -> str:
        return tenant_key(tenant_id, "ai", "usage", day.isoformat())

    def _monthly_key(self, tenant_id: uuid.UUID, month_str: str) -> str:
        return tenant_key(tenant_id, "ai", "usage", month_str)

    async def can_consume(self, tenant_id: uuid.UUID, tokens: int, tier: Optional[str] = None) -> bool:
        plan = get_plan(tier) if tier else None
        daily_quota = plan.daily_tokens if plan else self.default_daily_quota
        monthly_quota = plan.monthly_tokens if plan else daily_quota * 30

        day = dt.date.today()
        month = dt.date(day.year, day.month, 1).isoformat()
        
        daily_key = self._daily_key(tenant_id, day)
        monthly_key = self._monthly_key(tenant_id, month)
        
        try:
            # Check daily
            daily_used_raw = await redis_client.hget(daily_key, "total_tokens")
            daily_used = int(daily_used_raw) if daily_used_raw else 0
            if (daily_used + max(tokens, 0)) > daily_quota:
                return False
                
            # Check monthly
            monthly_used_raw = await redis_client.hget(monthly_key, "total_tokens")
            monthly_used = int(monthly_used_raw) if monthly_used_raw else 0
            if (monthly_used + max(tokens, 0)) > monthly_quota:
                return False
                
            return True
        except Exception:
            # Fail open in production if redis is down, or log error
            return True

    async def track(
        self,
        tenant_id: uuid.UUID,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        provider: str,
        had_error: bool,
    ) -> None:
        day = dt.date.today()
        month = dt.date(day.year, day.month, 1).isoformat()
        daily_key = self._daily_key(tenant_id, day)
        monthly_key = tenant_key(tenant_id, "ai", "usage", month)
        total = max(prompt_tokens, 0) + max(completion_tokens, 0)
        try:
            pipe = redis_client.pipeline()
            for key in (daily_key, monthly_key):
                pipe.hincrby(key, "prompt_tokens", max(prompt_tokens, 0))
                pipe.hincrby(key, "completion_tokens", max(completion_tokens, 0))
                pipe.hincrby(key, "total_tokens", total)
                pipe.hincrby(key, "requests", 1)
                pipe.hincrbyfloat(key, "latency_ms_total", max(latency_ms, 0.0))
                if had_error:
                    pipe.hincrby(key, "errors", 1)
                pipe.hset(key, "provider", provider)
                pipe.expire(key, 90 * 24 * 3600)
            await pipe.execute()
        except Exception:
            return
