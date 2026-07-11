import uuid
import datetime as dt
import logging
from typing import Dict, Any, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant, TenantStatus, User, UserRole, UserStatus
from app.services.onboarding_analytics_service import OnboardingAnalyticsService
from app.services.analytics.operational_insights_service import OperationalInsightsService
from app.services.notification_service import NotificationService
from app.services.follow_up_service import FollowUpService

logger = logging.getLogger(__name__)

class GrowthAutomationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.onboarding_svc = OnboardingAnalyticsService(db)
        self.ops_svc = OperationalInsightsService(db)
        self.notif_svc = NotificationService(db)

    async def run_onboarding_rescue_workflow(self) -> Dict[str, Any]:
        """Identify tenants stuck in onboarding and trigger deterministic interventions."""
        # 1. Fetch tenants in TRIAL status
        stmt = select(Tenant).where(Tenant.status == TenantStatus.TRIAL)
        result = await self.db.execute(stmt)
        tenants = result.scalars().all()
        
        interventions = 0
        for t in tenants:
            stats = await self.onboarding_svc.get_tenant_onboarding_stats(t.id)
            
            # Condition: Stuck for > 48h with score < 50
            if stats["activation_score"] < 50 and t.created_at < dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=48):
                # Check if we already sent a rescue notification recently
                if await self._should_trigger_rescue(t.id, "onboarding_rescue"):
                    await self._trigger_onboarding_rescue(t, stats)
                    interventions += 1
                    
        return {"onboarding_rescue_triggers": interventions}

    async def run_retention_rescue_workflow(self) -> Dict[str, Any]:
        """Identify active tenants with declining engagement and trigger success alerts."""
        risk_dashboard = await self.ops_svc.get_retention_risk_dashboard()
        
        interventions = 0
        for risk in risk_dashboard:
            if risk["risk_level"] == "HIGH":
                tenant_id = risk["tenant_id"]
                if await self._should_trigger_rescue(tenant_id, "retention_rescue"):
                    await self._trigger_retention_rescue(tenant_id, risk)
                    interventions += 1
                    
        return {"retention_rescue_triggers": interventions}

    async def _should_trigger_rescue(self, tenant_id: uuid.UUID, rescue_type: str) -> bool:
        """Rate limit rescue interventions to avoid spam (e.g., once every 7 days)."""
        # Heuristic: Check settings/metadata for last rescue timestamp
        tenant = await self.db.get(Tenant, tenant_id)
        last_rescue = tenant.settings.get(f"last_{rescue_type}_at")
        
        if last_rescue:
            last_dt = dt.datetime.fromisoformat(last_rescue)
            if last_dt > dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7):
                return False
        return True

    async def _trigger_onboarding_rescue(self, tenant: Tenant, stats: Dict[str, Any]):
        """Execute the intervention for a stuck onboarding flow."""
        # 1. Find the admin user
        user_stmt = select(User).where(and_(User.tenant_id == tenant.id, User.role == UserRole.BUSINESS_ADMIN))
        user_res = await self.db.execute(user_stmt)
        admin = user_res.scalar_one_or_none()
        
        if not admin: return

        # 2. Get recommendations
        recs = await self.onboarding_svc.get_onboarding_recommendations(tenant.id)
        rec_text = "\n".join([f"- {r}" for r in recs])

        # 3. Send Notification
        await self.notif_svc.send_email_notification(
            tenant_id=tenant.id,
            recipient=admin.email,
            subject="Ready to launch your AI Appointment Setter?",
            content=f"Hi {admin.full_name},\n\nWe noticed you're almost there with your setup! To get your AI live, we recommend:\n{rec_text}\n\nNeed help? Just reply to this email.",
            user_id=admin.id
        )

        # 4. Record the intervention
        if not tenant.settings: tenant.settings = {}
        tenant.settings["last_onboarding_rescue_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        await self.db.commit()
        
        logger.info("onboarding_rescue_triggered", tenant_id=str(tenant.id), admin_email=admin.email)

    async def _trigger_retention_rescue(self, tenant_id: uuid.UUID, risk_data: Dict[str, Any]):
        """Execute the intervention for a high-risk churn tenant (Internal Alert)."""
        # For high-risk churn, we alert the internal success team instead of the customer directly
        # In a real app, this might go to Slack or a CRM task
        
        # 1. Create a SupportIssue or Internal Follow-up for the Founder/CS
        from app.models.support import SupportIssue, SupportIssueType, SupportIssueStatus, SupportIssuePriority
        
        issue = SupportIssue(
            tenant_id=tenant_id,
            title=f"CHURN RISK: {risk_data['business_name']}",
            description=f"Engagement trend: {risk_data['engagement_trend']}. Active days (30d): {risk_data['active_days_30d']}. Manual intervention required.",
            issue_type=SupportIssueType.ONBOARDING_FRICTION, # Using existing type or adding new
            status=SupportIssueStatus.OPEN,
            priority=SupportIssuePriority.URGENT
        )
        self.db.add(issue)
        
        tenant = await self.db.get(Tenant, tenant_id)
        if not tenant.settings: tenant.settings = {}
        tenant.settings["last_retention_rescue_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        
        await self.db.commit()
        logger.warning("retention_rescue_triggered", tenant_id=str(tenant_id), risk_level="HIGH")
