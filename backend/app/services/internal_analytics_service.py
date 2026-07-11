import uuid
import datetime as dt
from typing import Dict, Any, List
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    Tenant, Conversation, Message, Appointment, 
    WorkflowExecution, WorkflowExecutionStatus
)

class InternalAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def platform_sla_metrics(self) -> Dict[str, Any]:
        """Global platform SLA and performance metrics."""
        # AI Response Latency (Aggregated from Observability if available, or just mock here)
        # For now, let's look at Workflow success rate
        
        total_workflows = await self.db.execute(select(func.count(WorkflowExecution.id)))
        success_workflows = await self.db.execute(
            select(func.count(WorkflowExecution.id)).where(WorkflowExecution.status == WorkflowExecutionStatus.COMPLETED)
        )
        
        total = total_workflows.scalar() or 0
        success = success_workflows.scalar() or 0
        workflow_success_rate = (success / total * 100) if total > 0 else 100.0
        
        return {
            "workflow_success_rate": round(workflow_success_rate, 2),
            "api_uptime_pct": 99.9, # Mock
            "avg_ai_latency_ms": 1200, # Mock
        }

    async def get_booking_conversion_stats(self) -> Dict[str, Any]:
        """Platform-wide booking conversion funnel."""
        # Conversations -> Appointments
        total_convs = await self.db.execute(select(func.count(Conversation.id)))
        total_bookings = await self.db.execute(select(func.count(Appointment.id)))
        
        convs = total_convs.scalar() or 0
        bookings = total_bookings.scalar() or 0
        
        conversion_rate = (bookings / convs * 100) if convs > 0 else 0.0
        
        return {
            "total_conversations": convs,
            "total_bookings": bookings,
            "conversion_rate": round(conversion_rate, 2),
        }

    async def tenant_engagement_ranking(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Tenants with highest activity in last 30 days."""
        since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
        
        stmt = (
            select(Tenant.business_name, func.count(Conversation.id).label("activity"))
            .join(Conversation, Conversation.tenant_id == Tenant.id)
            .where(Conversation.created_at >= since)
            .group_by(Tenant.business_name)
            .order_by(text("activity DESC"))
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return [{"name": row.business_name, "conversations": row.activity} for row in result]

    async def feature_adoption_analytics(self) -> Dict[str, Any]:
        """Analyze which AI workflows or CRM integrations are being adopted."""
        total_tenants = await self.db.execute(select(func.count(Tenant.id)))
        tenants = total_tenants.scalar() or 0
        if tenants == 0:
            return {"active_tenants": 0}
            
        # Example heuristic: how many tenants have customized their AI prompt
        from app.models import AIConfiguration
        custom_ai = await self.db.execute(select(func.count(AIConfiguration.id)).where(AIConfiguration.system_prompt != None))
        custom_ai_count = custom_ai.scalar() or 0
        
        return {
            "active_tenants": tenants,
            "ai_customization_adoption_pct": round((custom_ai_count / tenants * 100), 2),
        }

    async def get_churn_prediction_indicators(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Evaluate a specific tenant's likelihood to churn."""
        since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)
        recent_activity = await self.db.execute(
            select(func.count(Conversation.id))
            .where(Conversation.tenant_id == tenant_id, Conversation.created_at >= since)
        )
        activity_count = recent_activity.scalar() or 0
        
        return {
            "tenant_id": tenant_id,
            "recent_activity_7d": activity_count,
            "churn_risk": "HIGH" if activity_count == 0 else ("MEDIUM" if activity_count < 5 else "LOW")
        }

    async def pricing_intelligence(self) -> Dict[str, Any]:
        """Global pricing and plan utilization analytics."""
        stmt = select(Tenant.subscription_tier, func.count(Tenant.id)).group_by(Tenant.subscription_tier)
        result = await self.db.execute(stmt)
        utilization = {tier: count for tier, count in result.all()}
        
        return {
            "plan_utilization": utilization,
            "total_tenants": sum(utilization.values())
        }

    async def quota_pressure_analytics(self) -> List[Dict[str, Any]]:
        """Identify tenants approaching their plan limits."""
        # Example heuristic: checking AI token usage vs limits (simplified)
        from app.core.billing import get_plan
        from app.core.redis import redis_client
        from app.core.redis_keys import tenant_key
        
        tenants = await self.db.execute(select(Tenant).where(Tenant.status == "active"))
        tenants_list = tenants.scalars().all()
        
        pressure_list = []
        day = dt.date.today().isoformat()
        
        for t in tenants_list:
            plan = get_plan(t.subscription_tier)
            key = tenant_key(t.id, "ai", "usage", day)
            used = await redis_client.hget(key, "total_tokens")
            used_int = int(used) if used else 0
            
            usage_pct = (used_int / plan.daily_tokens * 100) if plan.daily_tokens > 0 else 0
            if usage_pct > 80:
                pressure_list.append({
                    "tenant_id": t.id,
                    "business_name": t.business_name,
                    "usage_pct": round(usage_pct, 2),
                    "tier": t.subscription_tier
                })
        return pressure_list

    async def pmf_activation_rate(self) -> Dict[str, Any]:
        """Platform-wide PMF activation rate analysis."""
        from app.services.onboarding_analytics_service import OnboardingAnalyticsService
        onboarding_svc = OnboardingAnalyticsService(self.db)
        
        total_tenants = await self.db.execute(select(func.count(Tenant.id)))
        total = total_tenants.scalar() or 0
        if total == 0:
            return {"activation_rate": 0}
            
        activated_count = 0
        tenants = await self.db.execute(select(Tenant.id))
        for t_id in tenants.scalars().all():
            stats = await onboarding_svc.get_tenant_onboarding_stats(t_id)
            if stats["is_activated"]:
                activated_count += 1
                
        return {
            "total_tenants": total,
            "activated_tenants": activated_count,
            "activation_rate_pct": round((activated_count / total * 100), 2)
        }

    async def get_tenant_engagement_score(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Calculate a 0-100 engagement score for a tenant."""
        # Heuristics:
        # - 40 points: Onboarding completeness
        # - 30 points: Conversation volume (last 30d)
        # - 30 points: Booking conversion rate
        
        from app.services.onboarding_analytics_service import OnboardingAnalyticsService
        onboarding_svc = OnboardingAnalyticsService(self.db)
        onboarding_stats = await onboarding_svc.get_tenant_onboarding_stats(tenant_id)
        onboarding_pts = onboarding_stats["activation_score"] * 0.4 
        
        since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
        conv_count = await self.db.execute(
            select(func.count(Conversation.id)).where(Conversation.tenant_id == tenant_id, Conversation.created_at >= since)
        )
        conversations = conv_count.scalar() or 0
        conv_pts = min(conversations, 30) 
        
        tenant_bookings = await self.db.execute(
            select(func.count(Appointment.id)).where(Appointment.tenant_id == tenant_id, Appointment.created_at >= since)
        )
        bookings = tenant_bookings.scalar() or 0
        conversion_rate = (bookings / conversations) if conversations > 0 else 0
        conversion_pts = min(conversion_rate * 100, 30)
        
        total_score = onboarding_pts + conv_pts + conversion_pts
        
        return {
            "tenant_id": tenant_id,
            "engagement_score": round(total_score, 2),
            "recommendation": "UPGRADE" if total_score > 80 else ("ASSIST" if total_score < 40 else "NURTURE")
        }

    async def experiment_performance_summary(self, experiment_name: str) -> Dict[str, Any]:
        """Compare activation rates and conversion across experiment variants."""
        from app.models.experiment import TenantExperimentAssignment
        from app.services.onboarding_analytics_service import OnboardingAnalyticsService
        onboarding_svc = OnboardingAnalyticsService(self.db)
        
        assignments = await self.db.execute(
            select(TenantExperimentAssignment).where(TenantExperimentAssignment.experiment_name == experiment_name)
        )
        rows = assignments.scalars().all()
        
        variants_data = {} # {variant_name: {total: 0, activated: 0}}
        
        for r in rows:
            if r.variant_name not in variants_data:
                variants_data[r.variant_name] = {"total": 0, "activated": 0}
            
            variants_data[r.variant_name]["total"] += 1
            stats = await onboarding_svc.get_tenant_onboarding_stats(r.tenant_id)
            if stats["is_activated"]:
                variants_data[r.variant_name]["activated"] += 1
                
        results = {}
        for v, data in variants_data.items():
            rate = (data["activated"] / data["total"] * 100) if data["total"] > 0 else 0
            results[v] = {
                "sample_size": data["total"],
                "activation_rate_pct": round(rate, 2)
            }
        return results
