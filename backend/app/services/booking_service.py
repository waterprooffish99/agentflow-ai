import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.idempotency import IdempotencyService
from app.core.tenant_guard import assert_tenant_match
from app.models import Appointment, AppointmentStatus, BookingEvent, Customer, StaffMember
from app.services.quota_service import QuotaEnforcerService

logger = logging.getLogger(__name__)

class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.idempotency = IdempotencyService(ttl_seconds=4 * 3600)

    async def create_appointment(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        service_type: str,
        start_time: datetime,
        end_time: datetime,
        lead_id: Optional[uuid.UUID] = None,
        staff_member_id: Optional[uuid.UUID] = None,
        notes: Optional[str] = None,
        actor_type: str = "ai",
        actor_id: Optional[uuid.UUID] = None,
    ) -> Appointment:
        """Create a new appointment and log the event."""
        # 0. Enforce Quota
        quota = QuotaEnforcerService(self.db)
        if not await quota.can_add_booking(tenant_id):
            raise ValueError("monthly_booking_quota_exceeded")

        # 1. Enforce tenant ownership for referenced resources.
        cust_result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id, Customer.tenant_id == tenant_id)
        )
        customer = cust_result.scalar_one_or_none()
        if not customer:
            raise ValueError("Customer not found for tenant")

        idem_payload = {
            "customer_id": str(customer_id),
            "service_type": service_type,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "lead_id": str(lead_id) if lead_id else None,
            "staff_member_id": str(staff_member_id) if staff_member_id else None,
        }
        can_create = await self.idempotency.acquire(tenant_id, "booking.create", idem_payload)
        if not can_create:
            existing = await self.db.execute(
                select(Appointment).where(
                    Appointment.tenant_id == tenant_id,
                    Appointment.customer_id == customer_id,
                    Appointment.start_time == start_time,
                    Appointment.end_time == end_time,
                )
            )
            found = existing.scalar_one_or_none()
            if found:
                return found
            raise ValueError("Duplicate booking request blocked")

        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            lead_id=lead_id,
            staff_member_id=staff_member_id,
            service_type=service_type,
            start_time=start_time,
            end_time=end_time,
            status=AppointmentStatus.CONFIRMED,
            notes=notes,
        )
        self.db.add(appointment)
        await self.db.flush()

        # Log event
        event = BookingEvent(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
            event_type="created",
            actor_type=actor_type,
            actor_id=actor_id,
            description=f"Appointment created for {service_type}",
        )
        self.db.add(event)
        await self.db.flush()

        return appointment

    async def cancel_appointment(
        self,
        appointment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        reason: Optional[str] = None,
        actor_type: str = "customer",
        actor_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Cancel an appointment."""
        result = await self.db.execute(
            select(Appointment).where(
                Appointment.id == appointment_id,
                Appointment.tenant_id == tenant_id
            )
        )
        appointment = result.scalar_one_or_none()
        if not appointment or appointment.status == AppointmentStatus.CANCELLED:
            return False
        assert_tenant_match(appointment.tenant_id, tenant_id)

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_reason = reason
        appointment.cancelled_by = actor_id if actor_type == "user" else None
        
        # Log event
        event = BookingEvent(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
            event_type="cancelled",
            actor_type=actor_type,
            actor_id=actor_id,
            description=f"Appointment cancelled: {reason}",
        )
        self.db.add(event)
        await self.db.flush()
        
        return True

    async def reschedule_appointment(
        self,
        appointment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        new_start_time: datetime,
        new_end_time: datetime,
        reason: Optional[str] = None,
        actor_type: str = "ai",
        actor_id: Optional[uuid.UUID] = None,
    ) -> Optional[Appointment]:
        """Reschedule an existing appointment."""
        result = await self.db.execute(
            select(Appointment).where(
                Appointment.id == appointment_id,
                Appointment.tenant_id == tenant_id
            )
        )
        old_appointment = result.scalar_one_or_none()
        if not old_appointment:
            return None
        assert_tenant_match(old_appointment.tenant_id, tenant_id)

        # Create new appointment
        new_appointment = await self.create_appointment(
            tenant_id=tenant_id,
            customer_id=old_appointment.customer_id,
            service_type=old_appointment.service_type,
            start_time=new_start_time,
            end_time=new_end_time,
            lead_id=old_appointment.lead_id,
            staff_member_id=old_appointment.staff_member_id,
            notes=f"Rescheduled from {old_appointment.id}. Reason: {reason}",
            actor_type=actor_type,
            actor_id=actor_id,
        )
        
        # Link old to new
        old_appointment.status = AppointmentStatus.RESCHEDULED
        old_appointment.rescheduled_to_id = new_appointment.id
        new_appointment.rescheduled_from_id = old_appointment.id
        
        # Log event on old appointment
        event = BookingEvent(
            tenant_id=tenant_id,
            appointment_id=old_appointment.id,
            event_type="rescheduled",
            actor_type=actor_type,
            actor_id=actor_id,
            description=f"Rescheduled to {new_appointment.id}",
        )
        self.db.add(event)
        await self.db.flush()
        
        return new_appointment
