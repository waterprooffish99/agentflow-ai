import uuid
import datetime as dt
from typing import Dict, Any, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant, SubscriptionTier, TenantStatus, Conversation, Appointment, WorkflowExecution
from app.services.analytics.activation_analytics_service import ActivationAnalyticsService
from app.services.analytics.retention_analytics_service import RetentionAnalyticsService
from app.services.analytics.operational_insights_service import OperationalInsightsService
from app.services.analytics.pmf_learning_service import PMFLearningService
from app.services.analytics.conversion_analytics_service import ConversionAnalyticsService
from app.core.billing import get_plan

class FounderDashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_executive_summary(self) -> Dict[str, Any]:
        """Aggregate high-level KPIs for the Founder Executive Dashboard."""
        
        # 1. Revenue Metrics (MRR)
        tenants_stmt = select(Tenant.subscription_tier).where(Tenant.status == TenantStatus.ACTIVE)
        tenants_res = await self.db.execute(tenants_stmt)
        active_tiers = tenants_res.scalars().all()
        
        total_mrr = sum(get_plan(tier).price_monthly for tier in active_tiers)
        
        # 2. Active Tenant Counts
        total_tenants = len(active_tiers)
        
        # 3. Activation & Retention (Aggregated from sub-services)
        activation_svc = ActivationAnalyticsService(self.db)
        retention_svc = RetentionAnalyticsService(self.db)
        
        activation_trends = await activation_svc.get_global_activation_trends(days=30)
        retention_summary = await retention_svc.platform_retention_summary()
        
        # 4. Operational Health
        ops_svc = OperationalInsightsService(self.db)
        health = await ops_svc.platform_health_overview()
        anomalies = await ops_svc.detect_anomalies()
        
        # 5. Growth & PMF
        pmf_svc = PMFLearningService(self.db)
        pmf_profile = await pmf_svc.get_successful_tenant_profile()
        
        conversion_svc = ConversionAnalyticsService(self.db)
        funnel = await conversion_svc.platform_conversion_funnel()

        # 6. Customer Journey Summary
        journey_summary = await self.get_customer_journey_instrumentation()

        return {
            "mrr": round(total_mrr, 2),
            "active_tenants": total_tenants,
            "activation_rate_pct": activation_trends.get("activation_rate_pct", 0),
            "retention_metrics": {
                "avg_retention_pct": retention_summary.get("avg_retention_pct", 0),
                "high_risk_tenants": len(await ops_svc.get_retention_risk_dashboard())
            },
            "ops_health": health,
            "critical_anomalies": [a.model_dump(mode='json') for a in anomalies if a.severity == "CRITICAL"],
            "pmf_signals": pmf_profile,
            "conversion_funnel": funnel,
            "customer_journey": journey_summary,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat()
        }

    async def get_customer_journey_instrumentation(self) -> Dict[str, Any]:
        """Track deterministic lifecycle progression across all tenants."""
        now = dt.datetime.now(dt.timezone.utc)
        since_30d = now - dt.timedelta(days=30)

        # Visitor -> Signup (Signups in last 30d)
        new_signups = await self.db.execute(
            select(func.count(Tenant.id)).where(Tenant.created_at >= since_30d)
        )
        
        # Signup -> Onboarding -> Activated
        activated = await self.db.execute(
            select(func.count(Tenant.id)).where(
                and_(Tenant.activated_at != None, Tenant.activated_at >= since_30d)
            )
        )
        
        # Activated -> Paid
        converted = await self.db.execute(
            select(func.count(Tenant.id)).where(
                and_(Tenant.converted_at != None, Tenant.converted_at >= since_30d)
            )
        )

        signups_count = new_signups.scalar() or 0
        activated_count = activated.scalar() or 0
        converted_count = converted.scalar() or 0

        return {
            "last_30d": {
                "signups": signups_count,
                "activated": activated_count,
                "converted_paid": converted_count,
                "activation_velocity": round(activated_count / signups_count * 100, 2) if signups_count > 0 else 0,
                "conversion_velocity": round(converted_count / activated_count * 100, 2) if activated_count > 0 else 0
            }
        }

    async def get_attribution_insights(self) -> List[Dict[str, Any]]:
        """Analyze which acquisition channels are driving high-LTV tenants."""
        stmt = (
            select(
                Tenant.acquisition_channel,
                func.count(Tenant.id).label("tenant_count"),
                func.sum(func.case((Tenant.status == TenantStatus.ACTIVE, 1), else_=0)).label("active_count")
            )
            .group_by(Tenant.acquisition_channel)
            .order_by(func.count(Tenant.id).desc())
        )
        
        result = await self.db.execute(stmt)
        insights = []
        for row in result.all():
            insights.append({
                "channel": row.acquisition_channel or "unknown",
                "total_tenants": row.tenant_count,
                "active_tenants": row.active_count,
                "retention_rate": round(row.active_count / row.tenant_count * 100, 2) if row.tenant_count > 0 else 0
            })
        return insights
