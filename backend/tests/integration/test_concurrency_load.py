import uuid
import time
import asyncio
import pytest
from unittest.mock import patch
from app.models import Tenant, TenantStatus, SubscriptionTier, Conversation

@pytest.mark.asyncio
async def test_20_concurrent_chat_requests_do_not_block(db_session, client):
    # 1. Create a tenant and a conversation
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Concurrency Load Business",
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

    # 2. Mock process_chat_message.delay to return a mock task object instantly
    class MockTask:
        id = "mock-task-id-123"

    with patch("app.tasks.chat_tasks.process_chat_message.delay", return_value=MockTask()) as mock_delay:
        # Fire 20 concurrent chat requests
        start_time = time.perf_counter()
        
        async def send_req(i: int):
            return await client.post(
                "/api/v1/chat/message",
                json={
                    "conversation_id": str(conversation.id),
                    "tenant_id": str(tenant_id),
                    "content": f"Concurrent message {i}"
                },
                headers={"X-API-Key": "test-key"}
            )
            
        responses = await asyncio.gather(*(send_req(i) for i in range(20)))
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        print(f"\nTime to process 20 concurrent requests: {duration:.4f} seconds")
        
        # Assert all responses are HTTP 202 (Accepted)
        for response in responses:
            assert response.status_code == 202
            data = response.json()
            assert data["task_id"] == "mock-task-id-123"
            assert data["status"] == "queued"
            
        # Assert that it completes extremely fast (under 3.0 seconds), proving non-blocking
        assert duration < 3.0
        assert mock_delay.call_count == 20
