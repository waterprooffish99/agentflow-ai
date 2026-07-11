import pytest

from app.core.rate_limit import DistributedRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_fallback_on_redis_failure(monkeypatch) -> None:
    limiter = DistributedRateLimiter(limit=1, window_seconds=60)

    async def boom(*_args, **_kwargs):
        raise RuntimeError("redis down")

    monkeypatch.setattr("app.core.rate_limit.redis_client.incr", boom)

    ok, _ = await limiter.allow("k")
    blocked, retry = await limiter.allow("k")
    assert ok
    assert not blocked
    assert retry >= 1
