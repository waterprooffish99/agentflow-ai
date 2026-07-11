import uuid

from app.core.idempotency import IdempotencyService


def test_idempotency_key_is_deterministic() -> None:
    svc = IdempotencyService()
    tenant = uuid.uuid4()
    payload = {"a": 1, "b": "x"}
    k1 = svc.build_key(tenant, "booking.create", payload)
    k2 = svc.build_key(tenant, "booking.create", payload)
    assert k1 == k2
