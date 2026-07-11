import uuid
from datetime import datetime, time, timedelta, date
from typing import List, Tuple, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AvailabilityRule, 
    AvailabilityException, 
    Appointment, 
    AppointmentStatus,
    DayOfWeek,
    StaffMember
)

class AvailabilityEngineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_slots(
        self,
        tenant_id: uuid.UUID,
        start_date: date,
        end_date: date,
        service_duration_minutes: int = 30,
        staff_member_id: Optional[uuid.UUID] = None,
    ) -> List[Tuple[datetime, datetime]]:
        """Calculate available time slots across a date range."""
        # 1. Fetch all relevant rules, exceptions, and appointments
        # For simplicity, we'll fetch everything for the tenant in one go 
        # or filtered by staff_member_id if provided.
        
        rules_query = select(AvailabilityRule).where(AvailabilityRule.tenant_id == tenant_id)
        if staff_member_id:
            rules_query = rules_query.where(AvailabilityRule.staff_member_id == staff_member_id)
        rules_result = await self.db.execute(rules_query)
        rules = rules_result.scalars().all()

        exceptions_query = select(AvailabilityException).where(
            and_(
                AvailabilityException.tenant_id == tenant_id,
                AvailabilityException.start_time >= datetime.combine(start_date, time.min),
                AvailabilityException.end_time <= datetime.combine(end_date, time.max)
            )
        )
        if staff_member_id:
            exceptions_query = exceptions_query.where(AvailabilityException.staff_member_id == staff_member_id)
        exceptions_result = await self.db.execute(exceptions_query)
        exceptions = exceptions_result.scalars().all()

        appointments_query = select(Appointment).where(
            and_(
                Appointment.tenant_id == tenant_id,
                Appointment.status == AppointmentStatus.CONFIRMED,
                Appointment.start_time >= datetime.combine(start_date, time.min),
                Appointment.start_time <= datetime.combine(end_date, time.max)
            )
        )
        if staff_member_id:
            appointments_query = appointments_query.where(Appointment.staff_member_id == staff_member_id)
        appointments_result = await self.db.execute(appointments_query)
        appointments = appointments_result.scalars().all()

        # 2. Iterate through each day and calculate slots
        available_slots = []
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime("%A").lower()
            day_rules = [r for r in rules if r.day_of_week == day_name and r.is_available]
            
            for rule in day_rules:
                slot_start = datetime.combine(current_date, rule.start_time)
                rule_end = datetime.combine(current_date, rule.end_time)
                
                while slot_start + timedelta(minutes=service_duration_minutes) <= rule_end:
                    slot_end = slot_start + timedelta(minutes=service_duration_minutes)
                    
                    # Check against exceptions
                    is_blocked_by_exception = any(
                        ex.start_time.replace(tzinfo=None) < slot_end and ex.end_time.replace(tzinfo=None) > slot_start and not ex.is_available
                        for ex in exceptions
                    )
                    
                    # Check against existing appointments
                    is_booked = any(
                        app.start_time.replace(tzinfo=None) < slot_end and app.end_time.replace(tzinfo=None) > slot_start
                        for app in appointments
                    )
                    
                    if not is_blocked_by_exception and not is_booked:
                        available_slots.append((slot_start, slot_end))
                    
                    slot_start += timedelta(minutes=service_duration_minutes)
            
            current_date += timedelta(days=1)
            
        return available_slots

    async def is_slot_available(
        self,
        tenant_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        staff_member_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Check if a specific time slot is free."""
        # Simple implementation: check if the slot is in available_slots
        slots = await self.get_available_slots(
            tenant_id, 
            start_time.date(), 
            start_time.date(),
            staff_member_id=staff_member_id
        )
        st_naive = start_time.replace(tzinfo=None)
        et_naive = end_time.replace(tzinfo=None)
        return any(s[0].replace(tzinfo=None) == st_naive and s[1].replace(tzinfo=None) == et_naive for s in slots)
