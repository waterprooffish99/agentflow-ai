import asyncio
import uuid
import datetime as dt
from sqlalchemy import delete
from app.core.database import async_session_maker
from app.core.security import hash_password
from app.models import (
    Tenant, SubscriptionTier, TenantStatus,
    BusinessProfile, Service, AIConfiguration,
    AvailabilityRule, DayOfWeek, FAQEntry,
    User, UserRole, UserStatus
)

async def seed_al_huda():
    print("🎬 Seeding Al Huda Gallery Tenant...")
    tenant_id = uuid.UUID("88888888-8888-8888-8888-888888888888")
    
    async with async_session_maker() as db:
        # Clean up existing data if any
        print("Cleaning up old Al Huda Gallery data...")
        await db.execute(delete(User).where(User.tenant_id == tenant_id))
        await db.execute(delete(AvailabilityRule).where(AvailabilityRule.tenant_id == tenant_id))
        await db.execute(delete(FAQEntry).where(FAQEntry.tenant_id == tenant_id))
        await db.execute(delete(Service).where(Service.tenant_id == tenant_id))
        await db.execute(delete(AIConfiguration).where(AIConfiguration.tenant_id == tenant_id))
        await db.execute(delete(BusinessProfile).where(BusinessProfile.tenant_id == tenant_id))
        await db.execute(delete(Tenant).where(Tenant.id == tenant_id))
        await db.commit()
        
        # 1. Create Tenant
        tenant = Tenant(
            id=tenant_id,
            business_name="Al Huda Gallery",
            subscription_tier=SubscriptionTier.GROWTH,
            status=TenantStatus.ACTIVE,
            timezone="Asia/Karachi",
            settings={"demo_mode": True}
        )
        db.add(tenant)
        
        # Create Admin User for Al Huda Gallery
        user = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="demo@alhuda.gallery",
            password_hash=hash_password("demo-secure-pass-2026"),
            full_name="Al Huda Gallery Manager",
            role=UserRole.BUSINESS_ADMIN,
            status=UserStatus.ACTIVE,
            email_verified=True
        )
        db.add(user)
        
        # 2. Business Profile
        profile = BusinessProfile(
            tenant_id=tenant_id,
            description="We sell handmade Balochi dresses, bridal wear, and custom stitched outfits for women, serving customers in Pakistan and the Gulf region.",
            industry="Balochi cultural & premium handmade dress shop",
            address="Karachi, Pakistan",
            phone="+923001234567",
            website="https://alhuda.gallery"
        )
        db.add(profile)
        
        # 3. Services
        services = [
            Service(
                tenant_id=tenant_id,
                name="Ready-made Balochi dress",
                description="Premium ready-made Balochi cultural dress. Price range: PKR 5,000-15,000",
                price=10000.0,
                duration_minutes=30,
                is_active=True
            ),
            Service(
                tenant_id=tenant_id,
                name="Custom stitched bridal dress",
                description="Custom handmade and stitched Balochi bridal wear. Takes 2-3 weeks to complete. Price range: PKR 25,000-60,000",
                price=42500.0,
                duration_minutes=60,
                is_active=True
            ),
            Service(
                tenant_id=tenant_id,
                name="Fitting appointment",
                description="Free in-person fitting appointment at our showroom.",
                price=0.0,
                duration_minutes=30,
                is_active=True
            )
        ]
        db.add_all(services)
        
        # 4. AI Configuration
        ai_config = AIConfiguration(
            tenant_id=tenant_id,
            name="Al Huda Assistant",
            personality_traits={"friendly": True},
            model_name="gemini-2.5-flash",
            temperature=0.7,
            system_prompt=(
                "You are the friendly AI receptionist for Al Huda Gallery, a Balochi cultural & premium handmade dress shop. "
                "We sell handmade Balochi dresses, bridal wear, and custom stitched outfits for women, serving customers in Pakistan and the Gulf region.\n\n"
                "Your goals are:\n"
                "1. Answer questions about Al Huda Gallery's products and policies.\n"
                "2. Share details of our services (Ready-made Balochi dress: PKR 5,000-15,000; Custom stitched bridal dress: PKR 25,000-60,000, 2-3 weeks; Fitting appointment: Free, 30 mins).\n"
                "3. Assist with scheduling/booking fitting appointments or customized dress requests.\n"
                "4. Be friendly, polite, and helpful at all times.\n\n"
                "Policies & FAQs:\n"
                "- Shipping: We ship to UAE, Saudi Arabia, and other Gulf countries. Shipping takes 5-10 days.\n"
                "- Customization: Custom designs are available. Ask customers to share preferred colors and style during booking.\n"
                "- Operating hours: Open Monday to Saturday, 11:00 AM to 7:00 PM (Pakistan time). Closed Friday afternoons from 1:00 PM to 2:30 PM for prayers."
            ),
            tools_enabled={"check_availability": True, "create_booking": True, "get_business_services": True}
        )
        db.add(ai_config)
        
        # 5. Availability Rules
        days = [
            DayOfWeek.MONDAY,
            DayOfWeek.TUESDAY,
            DayOfWeek.WEDNESDAY,
            DayOfWeek.THURSDAY,
            DayOfWeek.SATURDAY
        ]
        for day in days:
            db.add(AvailabilityRule(
                tenant_id=tenant_id,
                day_of_week=day,
                start_time=dt.time(11, 0),
                end_time=dt.time(19, 0),
                is_available=True
            ))
            
        # Friday availability split (closed 1:00 PM to 2:30 PM):
        db.add(AvailabilityRule(
            tenant_id=tenant_id,
            day_of_week=DayOfWeek.FRIDAY,
            start_time=dt.time(11, 0),
            end_time=dt.time(13, 0),
            is_available=True
        ))
        db.add(AvailabilityRule(
            tenant_id=tenant_id,
            day_of_week=DayOfWeek.FRIDAY,
            start_time=dt.time(14, 30),
            end_time=dt.time(19, 0),
            is_available=True
        ))
        
        # 6. FAQs
        faqs = [
            FAQEntry(
                tenant_id=tenant_id,
                question="Do you ship internationally?",
                answer="Yes, we ship to UAE, Saudi Arabia, and other Gulf countries. Shipping takes 5-10 days.",
                category="Shipping"
            ),
            FAQEntry(
                tenant_id=tenant_id,
                question="Can I customize the design?",
                answer="Yes! Custom designs are available, please share your preferred colors and style during booking.",
                category="Customization"
            )
        ]
        db.add_all(faqs)
        
        await db.commit()
        print("✅ Al Huda Gallery tenant seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_al_huda())
