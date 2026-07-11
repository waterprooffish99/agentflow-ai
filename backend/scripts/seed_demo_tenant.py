import asyncio
import uuid
import datetime as dt
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models import (
    Tenant, User, UserRole, UserStatus, 
    BusinessProfile, Service, AIConfiguration, 
    AvailabilityRule, DayOfWeek, Customer, Lead, LeadStatus,
    Conversation, Message, MessageRole, Appointment, AppointmentStatus,
    SubscriptionTier
)
from app.core.security import hash_password

async def seed_demo_tenant():
    """Seed a realistic demo tenant for sales and commercial walkthroughs."""
    print("🎬 Seeding Demo Tenant for Commercial Launch...")
    
    async with async_session_maker() as db:
        # 1. Create Tenant
        demo_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        existing = await db.get(Tenant, demo_id)
        if existing:
            print("  ⚠️ Demo tenant already exists, skipping creation.")
            return

        tenant = Tenant(
            id=demo_id,
            business_name="Luxe Aesthetics & Spa",
            subscription_tier=SubscriptionTier.GROWTH,
            status="active",
            timezone="America/New_York",
            settings={"demo_mode": True}
        )
        db.add(tenant)
        
        # 2. Create Admin User
        user = User(
            id=uuid.uuid4(),
            tenant_id=demo_id,
            email="demo@luxeaesthetics.com",
            password_hash=hash_password("demo-secure-pass-2026"),
            full_name="Sarah Spa Director",
            role=UserRole.BUSINESS_ADMIN,
            status=UserStatus.ACTIVE,
            email_verified=True
        )
        db.add(user)
        
        # 3. Business Profile
        profile = BusinessProfile(
            tenant_id=demo_id,
            description="A high-end medical spa specializing in facial rejuvenation, laser treatments, and holistic wellness.",
            website="https://luxeaesthetics.local"
        )
        db.add(profile)
        
        # 4. Services
        services = [
            Service(tenant_id=demo_id, name="Consultation", duration_minutes=30, price=50.0),
            Service(tenant_id=demo_id, name="HydraFacial", duration_minutes=60, price=180.0),
            Service(tenant_id=demo_id, name="Botox Treatment", duration_minutes=45, price=350.0),
        ]
        db.add_all(services)
        
        # 5. AI Configuration
        ai_config = AIConfiguration(
            tenant_id=demo_id,
            personality_traits="Warm, professional, knowledgeable, and helpful.",
            model_name="gemini-2.0-flash",
            temperature=0.4
        )
        db.add(ai_config)
        
        # 6. Availability
        rules = [
            AvailabilityRule(tenant_id=demo_id, day_of_week=DayOfWeek.MONDAY, start_time=dt.time(9, 0), end_time=dt.time(17, 0)),
            AvailabilityRule(tenant_id=demo_id, day_of_week=DayOfWeek.TUESDAY, start_time=dt.time(9, 0), end_time=dt.time(17, 0)),
            AvailabilityRule(tenant_id=demo_id, day_of_week=DayOfWeek.WEDNESDAY, start_time=dt.time(9, 0), end_time=dt.time(17, 0)),
            AvailabilityRule(tenant_id=demo_id, day_of_week=DayOfWeek.THURSDAY, start_time=dt.time(10, 0), end_time=dt.time(19, 0)),
            AvailabilityRule(tenant_id=demo_id, day_of_week=DayOfWeek.FRIDAY, start_time=dt.time(9, 0), end_time=dt.time(16, 0)),
        ]
        db.add_all(rules)
        
        # 7. Seed realistic Conversations & Leads
        customer = Customer(tenant_id=demo_id, name="Jane Doe", email="jane@example.local", phone="+15551234567")
        db.add(customer)
        await db.flush()
        
        lead = Lead(tenant_id=demo_id, customer_id=customer.id, status=LeadStatus.BOOKED)
        db.add(lead)
        await db.flush()
        
        conv = Conversation(tenant_id=demo_id, customer_id=customer.id, lead_id=lead.id)
        db.add(conv)
        await db.flush()
        
        messages = [
            Message(conversation_id=conv.id, role=MessageRole.USER, content="Hi, I want to book a facial"),
            Message(conversation_id=conv.id, role=MessageRole.ASSISTANT, content="Hello! We'd love to help you with that. We offer HydraFacials and Oxygen Facials. Which one are you interested in?"),
            Message(conversation_id=conv.id, role=MessageRole.USER, content="HydraFacial please"),
        ]
        db.add_all(messages)
        
        appointment = Appointment(
            tenant_id=demo_id, 
            customer_id=customer.id, 
            service_type="HydraFacial",
            start_time=dt.datetime.now() + dt.timedelta(days=2),
            end_time=dt.datetime.now() + dt.timedelta(days=2, hours=1),
            status=AppointmentStatus.CONFIRMED,
            lead_id=lead.id
        )
        db.add(appointment)

        await db.commit()
        print("✅ Demo tenant 'Luxe Aesthetics' seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_demo_tenant())
