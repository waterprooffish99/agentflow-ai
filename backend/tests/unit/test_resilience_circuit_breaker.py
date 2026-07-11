import pytest

from app.core.resilience import CircuitBreaker


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_threshold() -> None:
    cb = CircuitBreaker(failure_threshold=2, reset_timeout_seconds=60)

    async def fail():
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        await cb.call("p", fail)
    with pytest.raises(RuntimeError):
        await cb.call("p", fail)
    with pytest.raises(RuntimeError, match="circuit_open"):
        await cb.call("p", fail)
