import uuid
import datetime as dt
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant
from app.schemas.analytics import ConversionMetrics
from app.services.internal_analytics_service import InternalAnalyticsService

class ConversionAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tenant_conversion_metrics(self, tenant_id: uuid.UUID) -> ConversionMetrics:
        """Analyze conversion potential for a specific tenant with refined TTFV weighting."""
        tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
        tenant = (await self.db.execute(tenant_stmt)).scalar_one_or_none()
        
        if not tenant:
            raise ValueError("Tenant not found")
            
        # 1. Base Score from Engagement
        internal_svc = InternalAnalyticsService(self.db)
        engagement = await internal_svc.get_tenant_engagement_score(tenant_id)
        score = engagement["engagement_score"]
        
        # 2. Time-to-First-Value (TTFV) Bonus
        # Tenants who book their first appointment in < 24h have much higher conversion potential.
        from app.services.analytics.activation_analytics_service import ActivationAnalyticsService
        activation_svc = ActivationAnalyticsService(self.db)
        activation = await activation_svc.get_tenant_activation_metrics(tenant_id)
        
        ttfv_bonus = 0
        if activation.time_to_first_value_hours:
            if activation.time_to_first_value_hours < 24:
                ttfv_bonus = 15 # +15% boost for rapid value realization
            elif activation.time_to_first_value_hours < 72:
                ttfv_bonus = 5
        
        # Combined probability
        probability = (score + ttfv_bonus) / 100.0
        probability = min(probability, 0.99) # Cap at 99% for potential
        
        if tenant.subscription_tier != "free":
            probability = 1.0 # Already converted
            
        return ConversionMetrics(
            tenant_id=tenant_id,
            current_tier=tenant.subscription_tier,
            conversion_probability=round(probability, 2)
        )

    async def platform_conversion_funnel(self) -> Dict[str, Any]:
        """Aggregate conversion metrics across the platform, bounded to last 90 days (SUPER_ADMIN only)."""
        since_90d = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)
        
        stmt = (
            select(Tenant.subscription_tier, func.count(Tenant.id))
            .where(Tenant.created_at >= since_90d)
            .group_by(Tenant.subscription_tier)
        )
        result = await self.db.execute(stmt)
        tier_counts = {row[0]: row[1] for row in result.all()}
        
        total = sum(tier_counts.values())
        paid_count = total - tier_counts.get("free", 0) - tier_counts.get("trial", 0)
        
        conversion_rate = (paid_count / total * 100) if total > 0 else 0
        
        return {
            "tier_distribution": tier_counts,
            "overall_conversion_rate_pct": round(conversion_rate, 2),
            "total_tenants": total,
            "total_paid_tenants": paid_count,
            "window_days": 90
        }
