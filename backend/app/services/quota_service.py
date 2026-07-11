import datetime as dt
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.billing import get_plan
from app.models import Appointment, Customer, Tenant
from app.services.feature_flag_service import FeatureFlagService


class QuotaEnforcerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.feature_flags = FeatureFlagService(db)

    async def can_add_booking(self, tenant_id: uuid.UUID) -> bool:
        """Check if tenant has remaining booking quota for the current month."""
        tenant_result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tenant_result.scalar_one()
        plan = get_plan(tenant.subscription_tier)

        # Calculate month start
        now = dt.datetime.now()
        month_start = dt.datetime(now.year, now.month, 1)

        query = select(func.count()).select_from(Appointment).where(
            Appointment.tenant_id == tenant_id,
            Appointment.created_at >= month_start
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0

        return count < plan.monthly_bookings

    async def can_add_contact(self, tenant_id: uuid.UUID) -> bool:
        """Check if tenant has remaining CRM contact quota."""
        tenant_result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tenant_result.scalar_one()
        plan = get_plan(tenant.subscription_tier)

        query = select(func.count()).select_from(Customer).where(
            Customer.tenant_id == tenant_id
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0

        return count < plan.max_contacts

    async def has_feature(self, tenant_id: uuid.UUID, feature_name: str) -> bool:
        """Check if tenant has access to a specific feature."""
        # 1. Check dynamic feature flags (rollouts/overrides)
        if await self.feature_flags.is_enabled(tenant_id, feature_name):
            return True

        # 2. Fallback to plan-based entitlements
        tenant_result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tenant_result.scalar_one()
        plan = get_plan(tenant.subscription_tier)

        if "*" in plan.features:
            return True
        return feature_name in plan.features
