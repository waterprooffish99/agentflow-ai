import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import async_session_maker
from app.models import Appointment, AppointmentStatus, Conversation, Customer, Lead, LeadStatus, Tenant

DEMO_TENANT_NAME = "Demo Dental Studio"


async def seed() -> None:
    async with async_session_maker() as db:
        tenant = (
            await db.execute(select(Tenant).where(Tenant.business_name == DEMO_TENANT_NAME))
        ).scalar_one_or_none()
        if not tenant:
            tenant = Tenant(id=uuid.uuid4(), business_name=DEMO_TENANT_NAME)
            db.add(tenant)
            await db.flush()

        now = datetime.now(timezone.utc)
        for i in range(12):
            customer = Customer(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                name=f"Demo Customer {i}",
                email=f"customer{i}@example.com",
                phone=f"+1555000{i:04d}",
                preferences={},
            )
            db.add(customer)
            await db.flush()

            lead = Lead(
                tenant_id=tenant.id,
                customer_id=customer.id,
                status=LeadStatus.BOOKED if i % 3 == 0 else LeadStatus.QUALIFIED,
                source="demo",
            )
            db.add(lead)
            await db.flush()

            conv = Conversation(tenant_id=tenant.id, lead_id=lead.id, status="active")
            db.add(conv)

            appt = Appointment(
                tenant_id=tenant.id,
                customer_id=lead.customer_id,
                lead_id=lead.id,
                service_type="Dental Consultation",
                start_time=now + timedelta(days=i),
                end_time=now + timedelta(days=i, minutes=30),
                status=AppointmentStatus.NO_SHOW if i % 5 == 0 else AppointmentStatus.CONFIRMED,
            )
            db.add(appt)

        await db.commit()
    print("Demo seed complete")


if __name__ == "__main__":
    asyncio.run(seed())
