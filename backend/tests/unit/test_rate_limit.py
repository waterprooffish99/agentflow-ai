import pytest

from app.core.rate_limit import SlidingWindowRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_blocks_after_limit() -> None:
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=60)
    ok1, _ = await limiter.allow("k")
    ok2, _ = await limiter.allow("k")
    ok3, retry = await limiter.allow("k")
    assert ok1 and ok2
    assert not ok3
    assert retry >= 1
