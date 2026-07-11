import asyncio
import uuid
import httpx
from sqlalchemy import delete
from app.core.database import async_session_maker
from app.models import Tenant, TenantStatus, SubscriptionTier, Conversation
from app.services.billing_service import BillingService

async def main():
    tenant_id = uuid.uuid4()
    convo_id = uuid.uuid4()
    
    print("--- STARTING MANUAL VERIFICATION FLOW ---")
    
    async with async_session_maker() as db:
        # Step 1: Create a test tenant (ACTIVE)
        print("Cleaning up any leftover test data first...")
        await db.execute(delete(Tenant).where(Tenant.business_name == "Manual Verify Business"))
        await db.commit()
        
        print(f"Step 1: Creating test tenant {tenant_id} as ACTIVE...")
        tenant = Tenant(
            id=tenant_id,
            business_name="Manual Verify Business",
            subscription_tier=SubscriptionTier.STARTER,
            status=TenantStatus.ACTIVE
        )
        db.add(tenant)
        
        # Create a test conversation
        conversation = Conversation(
            id=convo_id,
            tenant_id=tenant_id,
            status="active"
        )
        db.add(conversation)
        
        await db.commit()
        print("GOOD: Test tenant and conversation created successfully in database.")

    # Step 2: Try to use AI chat (ACTIVE tenant)
    print("\nStep 2: Sending a chat message as an ACTIVE tenant customer...")
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "http://127.0.0.1:8000/api/v1/chat/message",
            json={
                "conversation_id": str(convo_id),
                "tenant_id": str(tenant_id),
                "content": "Hello, I want to book an appointment"
            },
            headers={"X-API-Key": "change-me"}  # Matches PUBLIC_API_KEY in .env
        )
        print(f"Response status: {res.status_code}")
        print(f"Response JSON: {res.json()}")
        if res.status_code == 202:
            print("GOOD: Chat request accepted (HTTP 202) as expected.")
        else:
            print("BAD: Chat request failed.")

    # Step 3: Simulate "payment failed" event
    print("\nStep 3: Simulating a payment failed event for this tenant...")
    async with async_session_maker() as db:
        billing = BillingService(db)
        await billing.handle_payment_failed(tenant_id)
        # Fetch status to verify
        db_tenant = await db.get(Tenant, tenant_id)
        print(f"Tenant status in database: {db_tenant.status}")
        if db_tenant.status == TenantStatus.PAST_DUE:
            print("GOOD: Tenant status successfully changed to PAST_DUE in database.")
        else:
            print("BAD: Tenant status did not change.")

    # Step 4: Try to use AI chat (PAST_DUE tenant)
    print("\nStep 4: Trying to use chat again as the PAST_DUE tenant customer...")
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "http://127.0.0.1:8000/api/v1/chat/message",
            json={
                "conversation_id": str(convo_id),
                "tenant_id": str(tenant_id),
                "content": "Hello again, is it blocked?"
            },
            headers={"X-API-Key": "change-me"}
        )
        print(f"Response status: {res.status_code}")
        print(f"Response JSON: {res.json()}")
        if res.status_code == 402:
            print("GOOD: Chat request BLOCKED with HTTP 402 Payment Required, as expected!")
        else:
            print("BAD: Chat request was not blocked.")

    # Step 5: Simulate "payment succeeded" event
    print("\nStep 5: Simulating a payment succeeded event (recovery) for this tenant...")
    async with async_session_maker() as db:
        billing = BillingService(db)
        await billing.handle_payment_succeeded(tenant_id)
        db_tenant = await db.get(Tenant, tenant_id)
        print(f"Tenant status in database: {db_tenant.status}")
        if db_tenant.status == TenantStatus.ACTIVE:
            print("GOOD: Tenant status successfully restored to ACTIVE in database.")
        else:
            print("BAD: Tenant status did not change.")

    # Step 6: Try to use AI chat (ACTIVE again)
    print("\nStep 6: Trying to use chat one more time as the restored ACTIVE tenant...")
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "http://127.0.0.1:8000/api/v1/chat/message",
            json={
                "conversation_id": str(convo_id),
                "tenant_id": str(tenant_id),
                "content": "Is the system working now?"
            },
            headers={"X-API-Key": "change-me"}
        )
        print(f"Response status: {res.status_code}")
        print(f"Response JSON: {res.json()}")
        if res.status_code == 202:
            print("GOOD: Chat request successfully accepted (HTTP 202) again after payment recovery!")
        else:
            print("BAD: Chat request failed.")

    # Cleanup database
    print("\nCleaning up test data from database...")
    async with async_session_maker() as db:
        await db.execute(delete(Conversation).where(Conversation.tenant_id == tenant_id))
        await db.execute(delete(Tenant).where(Tenant.id == tenant_id))
        await db.commit()
    print("Cleanup completed successfully.")
    
    print("\n--- MANUAL VERIFICATION FLOW COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(main())
