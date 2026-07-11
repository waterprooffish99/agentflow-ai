from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.main import app


async def _fake_db():
    yield object()


def test_refresh_returns_new_access_token(monkeypatch) -> None:
    app.dependency_overrides[get_db] = _fake_db

    class FakeAuthService:
        def __init__(self, _db):
            pass

        async def refresh_access_token(self, _refresh_token):
            return ("new.access.token", 3600)

    monkeypatch.setattr("app.api.auth.AuthService", FakeAuthService)

    client = TestClient(app)
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": "r1"})

    assert res.status_code == 200
    assert res.json()["access_token"] == "new.access.token"
    assert res.json()["expires_in"] == 3600

    app.dependency_overrides = {}


def test_refresh_rejects_missing_token() -> None:
    client = TestClient(app)
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": ""})
    assert res.status_code == 401
