import asyncio
import time
import uuid
import httpx
from sqlalchemy import delete
from app.core.database import async_session_maker
from app.models import Tenant, TenantStatus, SubscriptionTier, Conversation

# Helper to log both to console and a file
def log_info(msg: str):
    print(msg)
    with open("verify_celery_load.log", "a") as f:
        f.write(msg + "\n")

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
        await asyncio.sleep(0.5)
    raise TimeoutError(f"Task {task_id} timed out")

async def main():
    # Clear log file
    with open("verify_celery_load.log", "w") as f:
        f.write("")

    tenant_id = uuid.uuid4()
    convo_id = uuid.uuid4()
    
    log_info("--- STARTING CELERY LOAD VERIFICATION ---")
    
    async with async_session_maker() as db:
        # Step 1: Clean and Create Tenant
        log_info("Cleaning leftover data...")
        await db.execute(delete(Tenant).where(Tenant.business_name == "Celery Load Business"))
        await db.commit()
        
        log_info(f"Creating test tenant {tenant_id}...")
        tenant = Tenant(
            id=tenant_id,
            business_name="Celery Load Business",
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
        # Test 1: Send 1 single chat message
        log_info("\nTest 1: Sending 1 single chat message...")
        start_time = time.perf_counter()
        
        # Enqueue request
        res = await client.post(
            "http://127.0.0.1:8000/api/v1/chat/message",
            json={
                "conversation_id": str(convo_id),
                "tenant_id": str(tenant_id),
                "content": "Hello, single test message."
            },
            headers={"X-API-Key": "change-me"}
        )
        
        if res.status_code != 202:
            log_info(f"BAD: Single request failed to enqueue: {res.status_code} - {res.text}")
            return
            
        task_id = res.json()["task_id"]
        log_info(f"Enqueued successfully. Task ID: {task_id}. Polling for result...")
        
        # Poll for completion
        task_result = await poll_task(client, task_id)
        duration = time.perf_counter() - start_time
        
        log_info(f"Single task finished in {duration:.4f} seconds.")
        log_info(f"AI Response: {task_result['result']['content']}")
        
        # Test 2: Send 20 concurrent chat messages
        log_info("\nTest 2: Sending 20 concurrent chat messages at the same time...")
        start_time = time.perf_counter()
        
        async def send_and_poll(i: int):
            # Enqueue request
            res = await client.post(
                "http://127.0.0.1:8000/api/v1/chat/message",
                json={
                    "conversation_id": str(convo_id),
                    "tenant_id": str(tenant_id),
                    "content": f"Load test message {i}"
                },
                headers={"X-API-Key": "change-me"}
            )
            if res.status_code != 202:
                raise RuntimeError(f"Request {i} failed to enqueue: {res.status_code}")
            
            task_id = res.json()["task_id"]
            # Poll for result
            return await poll_task(client, task_id)
            
        log_info("Firing 20 concurrent requests and waiting for all Celery tasks to finish...")
        results = await asyncio.gather(*(send_and_poll(i) for i in range(20)), return_exceptions=True)
        total_duration = time.perf_counter() - start_time
        
        successes = 0
        failures = 0
        for r in results:
            if isinstance(r, Exception):
                failures += 1
                log_info(f"Task failed with error: {r}")
            else:
                successes += 1
                
        log_info(f"\n20 Concurrent Tasks Results:")
        log_info(f"- Successes: {successes}/20")
        log_info(f"- Failures: {failures}/20")
        log_info(f"- Total duration for ALL 20 to complete: {total_duration:.4f} seconds")
        log_info(f"- Average duration per task: {total_duration / 20:.4f} seconds")

    # Cleanup database
    log_info("\nCleaning up test data...")
    async with async_session_maker() as db:
        await db.execute(delete(Conversation).where(Conversation.tenant_id == tenant_id))
        await db.execute(delete(Tenant).where(Tenant.id == tenant_id))
        await db.commit()
    log_info("Cleanup completed.")
    
    log_info("\n--- CELERY LOAD VERIFICATION COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(main())
