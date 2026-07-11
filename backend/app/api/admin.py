import datetime as dt
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.api import deps
from app.models import (
    AIConfiguration,
    Appointment,
    BusinessProfile,
    Conversation,
    FeatureFlag,
    Incident,
    Lead,
    Service,
    Tenant,
    User,
    UserRole,
)
from app.services.incident_service import IncidentService
from app.services.internal_analytics_service import InternalAnalyticsService
from app.services.onboarding_analytics_service import OnboardingAnalyticsService
from app.services.pilot_success_service import PilotSuccessService
from app.services.analytics.activation_analytics_service import ActivationAnalyticsService
from app.services.analytics.retention_analytics_service import RetentionAnalyticsService
from app.services.analytics.support_analytics_service import SupportAnalyticsService
from app.services.analytics.pmf_learning_service import PMFLearningService
from app.services.analytics.conversion_analytics_service import ConversionAnalyticsService
from app.services.analytics.operational_insights_service import OperationalInsightsService
from app.core.redis import redis_client
import json
from typing import Any

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/pilot/dashboard")
async def get_pilot_dashboard(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Real-time pilot monitoring dashboard."""
    service = PilotSuccessService(db)
    return await service.get_pilot_metrics()


@router.get("/pilot/friction")
async def get_pilot_friction(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Identified onboarding friction points for pilot users."""
    service = PilotSuccessService(db)
    return await service.get_onboarding_friction_summary()

from app.schemas.tenant import PlatformMetrics, TenantListItem

async def get_cached_insight(key: str):
    """Utility to retrieve cached admin insights from Redis."""
    cached = await redis_client.get(f"admin_insight:{key}")
    return json.loads(cached) if cached else None

async def set_cached_insight(key: str, data: Any, ttl: int = 3600):
    """Utility to cache admin insights in Redis."""
    await redis_client.set(f"admin_insight:{key}", json.dumps(data), ex=ttl)


@router.get("/metrics", response_model=PlatformMetrics)
async def get_platform_metrics(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide metrics for operations."""
    total_tenants = await db.execute(select(func.count(Tenant.id)))
    active_tenants = await db.execute(select(func.count(Tenant.id)).where(Tenant.status == "active"))
    total_leads = await db.execute(select(func.count(Lead.id)))
    total_bookings = await db.execute(select(func.count(Appointment.id)))
    total_conversations = await db.execute(select(func.count(Conversation.id)))

    return PlatformMetrics(
        total_tenants=total_tenants.scalar() or 0,
        active_tenants=active_tenants.scalar() or 0,
        total_leads=total_leads.scalar() or 0,
        total_bookings=total_bookings.scalar() or 0,
        total_conversations=total_conversations.scalar() or 0,
    )


@router.get("/tenants", response_model=List[TenantListItem])
async def list_tenants(
    db: deps.DBSession,
    limit: int = 50,
    offset: int = 0,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """List all tenants with high-level stats."""
    query = (
        select(
            Tenant.id,
            Tenant.business_name,
            Tenant.timezone,
            Tenant.subscription_tier,
            Tenant.status,
            Tenant.created_at,
        )
        .order_by(Tenant.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    tenants = result.all()

    tenant_items = []
    for t in tenants:
        # Get extra stats for each tenant
        leads_count = await db.execute(select(func.count(Lead.id)).where(Lead.tenant_id == t.id))
        bookings_count = await db.execute(
            select(func.count(Appointment.id)).where(Appointment.tenant_id == t.id)
        )

        tenant_items.append(
            TenantListItem(
                id=t.id,
                business_name=t.business_name,
                timezone=t.timezone,
                subscription_tier=t.subscription_tier,
                status=t.status,
                created_at=t.created_at,
                active_leads=leads_count.scalar() or 0,
                monthly_bookings=bookings_count.scalar() or 0,
            )
        )

    return tenant_items


@router.get("/onboarding/funnel")
async def get_onboarding_funnel(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide onboarding funnel analytics."""
    service = OnboardingAnalyticsService(db)
    return await service.list_onboarding_funnel()


@router.get("/incidents", response_model=List[dict])
async def list_incidents(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """List all recent platform incidents."""
    service = IncidentService(db)
    incidents = await service.list_active_incidents()
    return [
        {
            "id": i.id,
            "title": i.title,
            "severity": i.severity,
            "status": i.status,
            "component": i.component,
            "created_at": i.created_at,
        }
        for i in incidents
    ]


@router.get("/feature-flags", response_model=List[dict])
async def list_feature_flags(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """List all global feature flags."""
    stmt = select(FeatureFlag).order_by(FeatureFlag.name)
    result = await db.execute(stmt)
    flags = result.scalars().all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "status": f.status,
            "rollout_percentage": f.rollout_percentage,
            "allowed_tiers": f.allowed_tiers,
        }
        for f in flags
    ]


@router.get("/analytics/conversions")
async def get_conversion_analytics(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide conversion analytics."""
    service = InternalAnalyticsService(db)
    return await service.get_booking_conversion_stats()


@router.get("/analytics/sla")
async def get_sla_metrics(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide SLA metrics."""
    service = InternalAnalyticsService(db)
    return await service.platform_sla_metrics()


@router.get("/analytics/pricing")
async def get_pricing_analytics(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Global pricing and plan utilization."""
    service = InternalAnalyticsService(db)
    return await service.pricing_intelligence()


@router.get("/analytics/quota-pressure")
async def get_quota_pressure(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Identify tenants near their limits."""
    service = InternalAnalyticsService(db)
    return await service.quota_pressure_analytics()


@router.get("/analytics/pmf-activation")
async def get_pmf_activation(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """PMF activation rate analytics."""
    service = InternalAnalyticsService(db)
    return await service.pmf_activation_rate()


@router.get("/analytics/experiments/{name}")
async def get_experiment_analytics(
    name: str,
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Compare performance across variants of a growth experiment."""
    service = InternalAnalyticsService(db)
    return await service.experiment_performance_summary(name)


@router.get("/tenants/{tenant_id}/engagement")
async def get_tenant_engagement(
    tenant_id: uuid.UUID,
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Detailed engagement score and retention recommendations."""
    service = InternalAnalyticsService(db)
    return await service.get_tenant_engagement_score(tenant_id)


@router.get("/analytics/feature-adoption")
async def get_feature_adoption(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide feature adoption and product intelligence."""
    service = InternalAnalyticsService(db)
    return await service.feature_adoption_analytics()


@router.get("/tenants/{tenant_id}/churn-risk")
async def get_churn_risk(
    tenant_id: uuid.UUID,
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Tenant-specific churn prediction and retention indicators."""
    service = InternalAnalyticsService(db)
    return await service.get_churn_prediction_indicators(tenant_id)


@router.get("/insights/activation-trends")
async def get_global_activation_trends(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
    days: int = 30,
):
    """Platform-wide activation trends and onboarding efficiency (Cached)."""
    cache_key = f"activation_trends:{days}"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await ActivationAnalyticsService(db).get_global_activation_trends(days)
    await set_cached_insight(cache_key, data)
    return data


@router.get("/insights/retention-summary")
async def get_global_retention_summary(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide retention cohort analysis (Cached)."""
    cache_key = "retention_summary"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await RetentionAnalyticsService(db).platform_retention_summary()
    await set_cached_insight(cache_key, data)
    return data


@router.get("/insights/support-analytics")
async def get_global_support_analytics(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide support workload and recurring friction patterns (Cached)."""
    cache_key = "support_analytics"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await SupportAnalyticsService(db).platform_support_analytics()
    await set_cached_insight(cache_key, data)
    return data


@router.get("/insights/pmf")
async def get_pmf_insights(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """PMF learning signals, vertical success, and feature correlations (Cached)."""
    cache_key = "pmf_insights"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await PMFLearningService(db).get_successful_tenant_profile()
    await set_cached_insight(cache_key, data)
    return data


@router.get("/insights/conversion-funnel")
async def get_global_conversion_funnel(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide commercial conversion funnel (Trial -> Paid) (Cached)."""
    cache_key = "conversion_funnel"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await ConversionAnalyticsService(db).platform_conversion_funnel()
    await set_cached_insight(cache_key, data)
    return data


@router.get("/insights/health")
async def get_operational_health(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """High-level platform health, DAU, and success rates (Cached)."""
    cache_key = "operational_health"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await OperationalInsightsService(db).platform_health_overview()
    await set_cached_insight(cache_key, data)
    return data


@router.get("/insights/anomalies")
async def get_operational_anomalies(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Detected operational anomalies and platform alerts (Cached)."""
    cache_key = "operational_anomalies"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await OperationalInsightsService(db).detect_anomalies()
    # Serialize Pydantic objects for cache
    serialized = [a.model_dump(mode='json') for a in data]
    await set_cached_insight(cache_key, serialized, ttl=300) # shorter TTL for anomalies
    return serialized


@router.get("/insights/retention-risk")
async def get_retention_risk_dashboard(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Identified tenants at high risk of churn for immediate intervention (Cached)."""
    cache_key = "retention_risk"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await OperationalInsightsService(db).get_retention_risk_dashboard()
    await set_cached_insight(cache_key, data, ttl=1800) # 30 min for risk
    return data


@router.get("/founder-dashboard")
async def get_founder_dashboard(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Unified executive operations dashboard for the founder (Cached)."""
    cache_key = "founder_summary"
    cached = await get_cached_insight(cache_key)
    if cached: return cached
    
    data = await FounderDashboardService(db).get_executive_summary()
    await set_cached_insight(cache_key, data, ttl=3600)
    return data


@router.get("/insights/attribution")
async def get_attribution_insights(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Acquisition channel and lead attribution analysis."""
    service = FounderDashboardService(db)
    return await service.get_attribution_insights()

from app.services.analytics.founder_dashboard_service import FounderDashboardService
