import asyncio
import time
import uuid
import httpx
from sqlalchemy import delete
from app.core.database import async_session_maker
from app.models import Tenant, TenantStatus, SubscriptionTier, Conversation

async def poll_task(client, task_id: str, timeout: int = 120) -> dict:
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        res = await client.get(
            f"http://127.0.0.1:8000/api/v1/chat/task/{task_id}",
            headers={"X-API-Key": "change-me"}
        )
        if res.status_code == 200:
            data = res.json()
            if data["status"] == "SUCCESS":
                return data
            elif data["status"] == "FAILURE":
                raise RuntimeError(f"Task {task_id} failed: {data}")
        await asyncio.sleep(0.2)
    raise TimeoutError(f"Task {task_id} timed out")

async def main():
    tenant_id = uuid.uuid4()
    convo_id = uuid.uuid4()
    
    print("--- STARTING SINGLE CHAT MESSAGE TEST ---")
    
    async with async_session_maker() as db:
        print("Cleaning leftover data...")
        await db.execute(delete(Tenant).where(Tenant.business_name == "Single Test Business"))
        await db.commit()
        
        print(f"Creating test tenant {tenant_id}...")
        tenant = Tenant(
            id=tenant_id,
            business_name="Single Test Business",
            subscription_tier=SubscriptionTier.STARTER,
            status=TenantStatus.ACTIVE
        )
        db.add(tenant)
        conversation = Conversation(
            id=convo_id,
            tenant_id=tenant_id,
            status="active"
        )
        db.add(conversation)
        await db.commit()

    async with httpx.AsyncClient(timeout=60.0) as client:
        print("\nSending 1 single chat message...")
        start_time = time.perf_counter()
        
        res = await client.post(
            "http://127.0.0.1:8000/api/v1/chat/message",
            json={
                "conversation_id": str(convo_id),
                "tenant_id": str(tenant_id),
                "content": "Hello, this is a single chat message load test."
            },
            headers={"X-API-Key": "change-me"}
        )
        
        if res.status_code != 202:
            print(f"FAILED to enqueue: {res.status_code} - {res.text}")
            return
            
        task_id = res.json()["task_id"]
        print(f"Enqueued successfully. Task ID: {task_id}. Polling...")
        
        task_result = await poll_task(client, task_id)
        duration = time.perf_counter() - start_time
        
        print(f"\nSingle task finished in {duration:.4f} seconds.")
        print(f"AI Response: {task_result['result']['content']}")

    print("\nCleaning up test data...")
    async with async_session_maker() as db:
        await db.execute(delete(Conversation).where(Conversation.tenant_id == tenant_id))
        await db.execute(delete(Tenant).where(Tenant.id == tenant_id))
        await db.commit()
    print("Cleanup completed.")
    print("--- SINGLE CHAT MESSAGE TEST COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(main())
