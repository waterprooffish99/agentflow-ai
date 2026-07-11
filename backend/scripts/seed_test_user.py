import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.services.auth_service import AuthService
from app.models import TenantStatus, UserStatus

async def seed_test_user():
    # TEST DATA
    EMAIL = "test@luxeaesthetics.com"
    PASSWORD = "test-secure-pass-2026"
    BUSINESS_NAME = "Luxe Aesthetics (Test)"
    FULL_NAME = "Test Admin"

    print(f"🌱 Seeding test user: {EMAIL}")

    async with async_session_maker() as db:
        auth_service = AuthService(db)
        
        try:
            # 1. Register Tenant and User
            tenant, user, _ = await auth_service.register_tenant(
                business_name=BUSINESS_NAME,
                email=EMAIL,
                password=PASSWORD,
                full_name=FULL_NAME
            )
            
            # 2. Automatically Verify and Activate
            user.email_verified = True
            user.status = UserStatus.ACTIVE
            tenant.status = TenantStatus.ACTIVE
            
            await db.commit()
            
            print("\n" + "✅"*20)
            print("TEST USER CREATED SUCCESSFULLY")
            print(f"Email:    {EMAIL}")
            print(f"Password: {PASSWORD}")
            print("✅"*20)
            print("\nYou can now go to http://localhost:3001/login and log in immediately!")

        except Exception as e:
            print(f"❌ Error seeding user: {e}")
            if "already exists" in str(e):
                print("Tip: Use a different email or reset your database.")

if __name__ == "__main__":
    asyncio.run(seed_test_user())
