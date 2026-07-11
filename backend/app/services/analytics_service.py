import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Appointment, AppointmentStatus, Conversation, Lead, LeadStatus


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def kpis(self, tenant_id: uuid.UUID) -> dict:
        lead_total = await self._count(Lead, tenant_id)
        booked_leads = await self._count(Lead, tenant_id, Lead.status == LeadStatus.BOOKED)
        appointments_total = await self._count(Appointment, tenant_id)
        no_shows = await self._count(
            Appointment, tenant_id, Appointment.status == AppointmentStatus.NO_SHOW
        )
        conversations = await self._count(Conversation, tenant_id)

        booking_conversion = (booked_leads / lead_total * 100) if lead_total else 0.0
        no_show_rate = (no_shows / appointments_total * 100) if appointments_total else 0.0
        return {
            "lead_total": lead_total,
            "booked_leads": booked_leads,
            "appointments_total": appointments_total,
            "conversations_total": conversations,
            "booking_conversion_pct": round(booking_conversion, 2),
            "no_show_rate_pct": round(no_show_rate, 2),
        }

    async def booking_trends(self, tenant_id: uuid.UUID, days: int = 30) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(func.date(Appointment.created_at).label("d"), func.count(Appointment.id).label("v"))
            .where(Appointment.tenant_id == tenant_id, Appointment.created_at >= since)
            .group_by("d")
            .order_by("d")
        )
        rows = (await self.db.execute(stmt)).all()
        return [{"date": str(r.d), "bookings": r.v} for r in rows]

    async def pipeline_analytics(self, tenant_id: uuid.UUID) -> list[dict]:
        stmt = (
            select(Lead.status, func.count(Lead.id))
            .where(Lead.tenant_id == tenant_id)
            .group_by(Lead.status)
        )
        rows = (await self.db.execute(stmt)).all()
        return [{"stage": status, "count": count} for status, count in rows]

    async def retention(self, tenant_id: uuid.UUID) -> dict:
        total_customers_stmt = select(func.count(func.distinct(Lead.customer_id))).where(
            Lead.tenant_id == tenant_id
        )
        repeat_customers_stmt = (
            select(func.count())
            .select_from(
                select(Lead.customer_id)
                .where(Lead.tenant_id == tenant_id)
                .group_by(Lead.customer_id)
                .having(func.count(Lead.id) > 1)
                .subquery()
            )
        )
        total = (await self.db.execute(total_customers_stmt)).scalar_one() or 0
        repeat = (await self.db.execute(repeat_customers_stmt)).scalar_one() or 0
        pct = (repeat / total * 100) if total else 0.0
        return {"customers_total": total, "repeat_customers": repeat, "repeat_rate_pct": round(pct, 2)}

    async def _count(self, model: type, tenant_id: uuid.UUID, *filters) -> int:
        stmt = select(func.count(model.id)).where(model.tenant_id == tenant_id, *filters)
        return (await self.db.execute(stmt)).scalar_one() or 0
