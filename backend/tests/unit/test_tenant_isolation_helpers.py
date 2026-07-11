import uuid

import pytest

from app.core.redis_keys import tenant_key
from app.core.tenant_guard import TenantIsolationError, assert_tenant_match


def test_tenant_key_namespacing() -> None:
    tenant_id = uuid.uuid4()
    key = tenant_key(tenant_id, "ai", "usage")
    assert key.startswith(f"tenant:{tenant_id}:")


def test_assert_tenant_match_raises() -> None:
    with pytest.raises(TenantIsolationError):
        assert_tenant_match(uuid.uuid4(), uuid.uuid4())
