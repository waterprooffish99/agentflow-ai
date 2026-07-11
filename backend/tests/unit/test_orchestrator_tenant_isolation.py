import uuid
from types import SimpleNamespace

import pytest

from app.services.ai_orchestrator_service import AIOrchestratorService


@pytest.mark.asyncio
async def test_orchestrator_rejects_cross_tenant_message() -> None:
    svc = AIOrchestratorService(db=SimpleNamespace())
    convo_tenant = uuid.uuid4()
    requested_tenant = uuid.uuid4()
    svc.conversation_service = SimpleNamespace(
        get_conversation=lambda _cid: SimpleNamespace(tenant_id=convo_tenant, customer_id=None),
    )

    async def _get_conversation(_cid, tenant_id=None):
        return SimpleNamespace(tenant_id=convo_tenant, customer_id=None)

    svc.conversation_service.get_conversation = _get_conversation

    with pytest.raises(ValueError, match="Tenant isolation violation"):
        await svc.handle_message(uuid.uuid4(), requested_tenant, "hello")
