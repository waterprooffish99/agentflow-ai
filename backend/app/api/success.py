import uuid
import datetime as dt
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.api import deps
from app.models import (
    Conversation,
    Lead,
    Tenant,
    User,
    UserRole,
)
from app.services.onboarding_analytics_service import OnboardingAnalyticsService

router = APIRouter(prefix="/success", tags=["customer_success"])

@router.get("/tenant-health")
async def list_tenants_health(
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Platform-wide tenant health for Customer Success."""
    tenants = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
    tenants_list = tenants.scalars().all()
    
    onboarding_service = OnboardingAnalyticsService(db)
    
    results = []
    for t in tenants_list:
        stats = await onboarding_service.get_tenant_onboarding_stats(t.id)
        
        #Engagement: Last activity
        last_conv = await db.execute(
            select(Conversation.created_at)
            .where(Conversation.tenant_id == t.id)
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )
        last_activity = last_conv.scalar()
        
        # Churn risk: Low score + no activity for 3 days
        is_at_risk = stats["activation_score"] < 50 and (
            not last_activity or last_activity < dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)
        )

        results.append({
            "tenant_id": t.id,
            "business_name": t.business_name,
            "tier": t.subscription_tier,
            "activation_score": stats["activation_score"],
            "last_activity": last_activity,
            "is_at_risk": is_at_risk,
            "onboarding_complete": stats["is_activated"],
        })
        
    return results
