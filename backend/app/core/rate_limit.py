import asyncio
import time
from collections import defaultdict, deque

from app.core.redis import redis_client
from app.core.redis_keys import tenant_key


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, key: str) -> tuple[bool, int]:
        now = time.time()
        async with self._lock:
            q = self._hits[key]
            while q and q[0] <= now - self.window_seconds:
                q.popleft()
            if len(q) >= self.limit:
                retry_after = int((q[0] + self.window_seconds) - now) + 1
                return False, max(retry_after, 1)
            q.append(now)
            return True, 0


class DistributedRateLimiter:
    """Redis-backed fixed-window limiter with in-memory fallback."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._fallback = SlidingWindowRateLimiter(limit=limit, window_seconds=window_seconds)

    async def allow(self, key: str) -> tuple[bool, int]:
        bucket = int(time.time() // self.window_seconds)
        redis_key = tenant_key("global", "ratelimit", key, str(bucket))
        try:
            current = await redis_client.incr(redis_key)
            if current == 1:
                await redis_client.expire(redis_key, self.window_seconds + 1)
            if current > self.limit:
                ttl = await redis_client.ttl(redis_key)
                return False, max(ttl, 1)
            return True, 0
        except Exception:
            # If Redis is unavailable, fail open with local limiter.
            return await self._fallback.allow(key)
