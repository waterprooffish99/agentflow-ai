import uuid
import datetime as dt
from typing import Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    Tenant, BusinessProfile, Service, AIConfiguration, 
    AvailabilityRule, Conversation, User
)

class OnboardingAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tenant_onboarding_stats(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Detailed onboarding progress for a tenant."""
        # Check components
        profile = await self.db.execute(select(BusinessProfile).where(BusinessProfile.tenant_id == tenant_id))
        has_profile = profile.scalar_one_or_none() is not None
        
        services_count = await self.db.execute(
            select(func.count(Service.id)).where(Service.tenant_id == tenant_id)
        )
        count_services = services_count.scalar() or 0
        
        ai_config = await self.db.execute(select(AIConfiguration).where(AIConfiguration.tenant_id == tenant_id))
        has_ai_config = ai_config.scalar_one_or_none() is not None
        
        availability = await self.db.execute(
            select(func.count(AvailabilityRule.id)).where(AvailabilityRule.tenant_id == tenant_id)
        )
        has_availability = (availability.scalar() or 0) > 0

        # Activation Score (0-100)
        # 40% for core setup, 60% for first engagement
        setup_score = sum([has_profile, count_services > 0, has_ai_config, has_availability]) * 10 # Max 40
        
        # Engagement: First conversation
        conv_count = await self.db.execute(
            select(func.count(Conversation.id)).where(Conversation.tenant_id == tenant_id)
        )
        has_conversations = (conv_count.scalar() or 0) > 0
        engagement_score = 60 if has_conversations else 0
        
        total_score = setup_score + engagement_score

        return {
            "setup": {
                "profile_complete": has_profile,
                "services_added": count_services,
                "ai_configured": has_ai_config,
                "availability_set": has_availability,
            },
            "activation_score": total_score,
            "is_activated": total_score >= 70, # Threshold for "activated" tenant
            "first_engagement": has_conversations,
        }

    async def list_onboarding_funnel(self) -> List[Dict[str, Any]]:
        """Platform-wide onboarding funnel analytics (Super Admin)."""
        tenants = await self.db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
        tenants_list = tenants.scalars().all()
        
        results = []
        for t in tenants_list:
            stats = await self.get_tenant_onboarding_stats(t.id)
            results.append({
                "tenant_id": t.id,
                "business_name": t.business_name,
                "created_at": t.created_at,
                "score": stats["activation_score"],
                "status": t.status,
            })
        return results

    async def get_onboarding_recommendations(self, tenant_id: uuid.UUID) -> List[str]:
        """Generate contextual guidance for tenants stuck in onboarding."""
        stats = await self.get_tenant_onboarding_stats(tenant_id)
        recs = []
        
        setup = stats["setup"]
        if not setup["profile_complete"]:
            recs.append("Add your business description to help the AI understand your brand.")
        if setup["services_added"] == 0:
            recs.append("List at least one service so customers can book appointments.")
        if not setup["ai_configured"]:
            recs.append("Customize your AI personality to match your business tone.")
        if not setup["availability_set"]:
            recs.append("Set your working hours to enable automated booking.")
        if not stats["first_engagement"]:
            recs.append("Try sending a test message to your AI to see it in action.")
            
        return recs
