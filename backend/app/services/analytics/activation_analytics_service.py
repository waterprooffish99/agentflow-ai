import uuid
import datetime as dt
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, Appointment, BusinessProfile, AIConfiguration, Service, AvailabilityRule
from app.schemas.analytics import ActivationMetrics
from app.services.analytics.utils import apply_tenant_filter, apply_date_window, safe_execute_query

class ActivationAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tenant_activation_metrics(self, tenant_id: uuid.UUID) -> ActivationMetrics:
        """Calculate detailed activation metrics for a specific tenant."""
        # 1. Check setup completion
        profile = await self.db.execute(select(BusinessProfile).where(BusinessProfile.tenant_id == tenant_id))
        has_profile = profile.scalar_one_or_none() is not None
        
        ai_config = await self.db.execute(select(AIConfiguration).where(AIConfiguration.tenant_id == tenant_id))
        has_ai_config = ai_config.scalar_one_or_none() is not None
        
        services = await self.db.execute(select(func.count(Service.id)).where(Service.tenant_id == tenant_id))
        has_services = (services.scalar() or 0) > 0
        
        availability = await self.db.execute(select(func.count(AvailabilityRule.id)).where(AvailabilityRule.tenant_id == tenant_id))
        has_availability = (availability.scalar() or 0) > 0
        
        # 2. Time to first value (First successful booking)
        tenant_stmt = select(Tenant.created_at).where(Tenant.id == tenant_id)
        tenant_created_at = (await self.db.execute(tenant_stmt)).scalar()
        
        first_booking_stmt = (
            select(Appointment.created_at)
            .where(Appointment.tenant_id == tenant_id)
            .order_by(Appointment.created_at.asc())
            .limit(1)
        )
        first_booking_at = (await self.db.execute(first_booking_stmt)).scalar()
        
        ttfv = None
        if tenant_created_at and first_booking_at:
            delta = first_booking_at - tenant_created_at
            ttfv = delta.total_seconds() / 3600 # hours
            
        # 3. Completion calculation
        setup_steps = [has_profile, has_ai_config, has_services, has_availability]
        completion_pct = (sum(setup_steps) / len(setup_steps)) * 100
        
        bottlenecks = []
        if not has_profile: bottlenecks.append("profile_setup")
        if not has_ai_config: bottlenecks.append("ai_configuration")
        if not has_services: bottlenecks.append("service_definition")
        if not has_availability: bottlenecks.append("availability_rules")
        
        return ActivationMetrics(
            tenant_id=tenant_id,
            time_to_first_value_hours=ttfv,
            onboarding_completion_pct=completion_pct,
            is_activated=completion_pct == 100 and ttfv is not None,
            bottlenecks=bottlenecks
        )

    async def get_global_activation_trends(self, days: int = 30) -> Dict[str, Any]:
        """Aggregate activation trends across all tenants (SUPER_ADMIN only)."""
        # This would be called by an admin endpoint
        tenants_stmt = apply_date_window(select(Tenant), Tenant.created_at, days)
        tenants = (await self.db.execute(tenants_stmt)).scalars().all()
        
        total_tenants = len(tenants)
        if total_tenants == 0:
            return {"avg_completion_pct": 0, "activation_rate": 0}
            
        total_completion = 0
        activated_count = 0
        
        for t in tenants:
            metrics = await self.get_tenant_activation_metrics(t.id)
            total_completion += metrics.onboarding_completion_pct
            if metrics.is_activated:
                activated_count += 1
                
        return {
            "total_new_tenants": total_tenants,
            "avg_completion_pct": round(total_completion / total_tenants, 2),
            "activation_rate_pct": round((activated_count / total_tenants) * 100, 2),
            "period_days": days
        }
