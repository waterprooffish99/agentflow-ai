import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


@dataclass
class CircuitState:
    failures: int = 0
    opened_at: float | None = None


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.reset_timeout_seconds = reset_timeout_seconds
        self._state: dict[str, CircuitState] = defaultdict(CircuitState)

    def _is_open(self, key: str) -> bool:
        s = self._state[key]
        if s.opened_at is None:
            return False
        if (time.time() - s.opened_at) > self.reset_timeout_seconds:
            s.failures = 0
            s.opened_at = None
            return False
        return True

    async def call(self, key: str, fn: Callable[[], Awaitable[T]]) -> T:
        if self._is_open(key):
            raise RuntimeError(f"circuit_open:{key}")
        try:
            result = await fn()
            self._state[key].failures = 0
            return result
        except Exception:
            s = self._state[key]
            s.failures += 1
            if s.failures >= self.failure_threshold:
                s.opened_at = time.time()
            raise


async def with_retry(
    fn: Callable[[], Awaitable[T]],
    attempts: int = 3,
    base_delay_seconds: float = 0.2,
    timeout_seconds: float = 10.0,
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await asyncio.wait_for(fn(), timeout=timeout_seconds)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == attempts:
                break
            await asyncio.sleep(base_delay_seconds * attempt)
    assert last_error is not None
    raise last_error
