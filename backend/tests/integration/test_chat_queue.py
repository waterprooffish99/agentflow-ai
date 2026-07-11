import uuid
import pytest
from app.models import Tenant, TenantStatus, SubscriptionTier, Conversation

@pytest.mark.asyncio
async def test_chat_message_flow_queued(db_session, client):
    # 1. Create a tenant and a conversation
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Test Business",
        subscription_tier=SubscriptionTier.STARTER,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()

    conversation = Conversation(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        status="active"
    )
    db_session.add(conversation)
    await db_session.flush()
    await db_session.commit()

    # 2. Call the chat message endpoint
    response = await client.post(
        "/api/v1/chat/message",
        json={
            "conversation_id": str(conversation.id),
            "tenant_id": str(tenant_id),
            "content": "Hello, I want to book an appointment"
        },
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["conversation_id"] == str(conversation.id)
    assert data["status"] == "queued"
    
    task_id = data["task_id"]

    # 3. Poll/check the status of the task
    status_response = await client.get(
        f"/api/v1/chat/task/{task_id}",
        headers={"X-API-Key": "test-key"}
    )
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["task_id"] == task_id
    assert status_data["status"] == "SUCCESS"
    assert "result" in status_data
    assert "content" in status_data["result"]
    assert "I'm here to help!" in status_data["result"]["content"]


@pytest.mark.asyncio
async def test_chat_stream_flow_queued(db_session, client):
    # 1. Create a tenant and a conversation
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Test Stream Business",
        subscription_tier=SubscriptionTier.STARTER,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()

    conversation = Conversation(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        status="active"
    )
    db_session.add(conversation)
    await db_session.flush()
    await db_session.commit()

    # 2. Call the chat stream endpoint
    response = await client.post(
        "/api/v1/chat/stream",
        json={
            "conversation_id": str(conversation.id),
            "tenant_id": str(tenant_id),
            "content": "Hello stream"
        },
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    content = response.text
    assert "data:" in content
    assert "I'm here to help!" in content
    assert "[DONE]" in content
