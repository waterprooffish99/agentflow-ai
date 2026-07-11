import uuid

from fastapi.testclient import TestClient

from app.api.deps import get_db, get_tenant_id
from app.main import app


async def _fake_db():
    yield object()


def _tenant_id() -> uuid.UUID:
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


def test_analytics_kpi_endpoint(monkeypatch) -> None:
    app.dependency_overrides[get_db] = _fake_db
    app.dependency_overrides[get_tenant_id] = _tenant_id

    class FakeAnalyticsService:
        def __init__(self, _db):
            pass

        async def kpis(self, _tenant_id):
            return {"lead_total": 10, "booking_conversion_pct": 40.0}

    monkeypatch.setattr("app.api.analytics.AnalyticsService", FakeAnalyticsService)

    client = TestClient(app)
    res = client.get("/api/v1/analytics/kpis")
    assert res.status_code == 200
    assert res.json()["lead_total"] == 10

    app.dependency_overrides = {}
