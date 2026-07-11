import asyncio
import datetime as dt
from sqlalchemy import select, text, func
from app.core.config import settings
from app.core.database import async_session_maker
from app.models import Tenant, Conversation
from app.services.onboarding_analytics_service import OnboardingAnalyticsService
from app.core.alerting import AlertManager
import structlog

logger = structlog.get_logger()

async def run_customer_success_automation():
    """Automated job to scan for churn risks and low engagement tenants."""
    logger.info("Starting Customer Success Automation job...")

    async with async_session_maker() as db:
        onboarding_service = OnboardingAnalyticsService(db)
        
        tenants = await db.execute(select(Tenant).where(Tenant.status == "active"))
        active_tenants = tenants.scalars().all()
        
        for tenant in active_tenants:
            # 1. Onboarding Intervention Check
            stats = await onboarding_service.get_tenant_onboarding_stats(tenant.id)
            
            # If tenant has been around for > 3 days but setup is incomplete
            age_days = (dt.datetime.now(dt.timezone.utc) - tenant.created_at).days
            if age_days > 3 and not stats["setup"]["profile_complete"]:
                logger.warning(
                    "onboarding_intervention_needed",
                    tenant_id=str(tenant.id),
                    business_name=tenant.business_name,
                    reason="Incomplete setup after 3 days"
                )
                # Could trigger an email via Customer Success tooling here

            # 2. Low Engagement / Churn Risk Check
            last_conv = await db.execute(
                select(Conversation.created_at)
                .where(Conversation.tenant_id == tenant.id)
                .order_by(Conversation.created_at.desc())
                .limit(1)
            )
            last_activity = last_conv.scalar()
            
            if last_activity and last_activity < dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7):
                logger.warning(
                    "tenant_inactivity_alert",
                    tenant_id=str(tenant.id),
                    business_name=tenant.business_name,
                    days_since_activity=(dt.datetime.now(dt.timezone.utc) - last_activity).days
                )
                # High priority alert if they are a paying customer
                if tenant.subscription_tier != "free":
                    await AlertManager.trigger_alert(
                        title="Paying Customer Churn Risk",
                        message=f"Tenant {tenant.business_name} has been inactive for > 7 days.",
                        severity="high",
                        component="customer_success",
                        context={"tenant_id": str(tenant.id), "tier": tenant.subscription_tier}
                    )

    logger.info("Customer Success Automation job completed.")

if __name__ == "__main__":
    asyncio.run(run_customer_success_automation())
