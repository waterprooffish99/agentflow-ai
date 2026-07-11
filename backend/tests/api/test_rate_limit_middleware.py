from fastapi.testclient import TestClient

from app.main import app


class BlockAllLimiter:
    async def allow(self, _key: str):
        return False, 2


def test_middleware_rate_limit(monkeypatch) -> None:
    monkeypatch.setattr("app.main.api_limiter", BlockAllLimiter())
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 429
    assert res.headers["Retry-After"] == "2"
