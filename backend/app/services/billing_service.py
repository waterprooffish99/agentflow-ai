import uuid
import logging
from typing import Optional, Dict, Any
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, SubscriptionTier, TenantStatus
from app.core.billing import get_plan
from app.core.config import settings

logger = logging.getLogger(__name__)

class BillingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        if settings.stripe_api_key:
            stripe.api_key = settings.stripe_api_key

    async def handle_subscription_updated(
        self, 
        tenant_id: uuid.UUID, 
        new_tier: str, 
        stripe_subscription_id: Optional[str] = None,
        new_status: Optional[TenantStatus] = None
    ) -> None:
        """Handle subscription lifecycle changes (typically from webhooks)."""
        tenant = await self.db.get(Tenant, tenant_id)
        if not tenant:
            logger.error(f"Tenant {tenant_id} not found for subscription update")
            return

        old_tier = tenant.subscription_tier
        try:
            tenant.subscription_tier = SubscriptionTier(new_tier.lower())
        except ValueError:
            logger.warning(f"Unknown tier {new_tier}, defaulting to FREE")
            tenant.subscription_tier = SubscriptionTier.FREE
        
        if new_status:
            tenant.status = new_status
        
        # Store metadata in settings
        if stripe_subscription_id:
            if not tenant.settings:
                tenant.settings = {}
            tenant.settings["stripe_subscription_id"] = stripe_subscription_id
            
        logger.info(
            "subscription_updated", 
            tenant_id=str(tenant_id), 
            old_tier=old_tier, 
            new_tier=tenant.subscription_tier,
            status=tenant.status
        )
        
        await self.db.commit()

    async def handle_payment_failed(self, tenant_id: uuid.UUID) -> None:
        """Mark tenant as past_due when payment fails."""
        tenant = await self.db.get(Tenant, tenant_id)
        if tenant:
            tenant.status = TenantStatus.PAST_DUE
            await self.db.commit()
            logger.warning(f"Tenant {tenant_id} marked as PAST_DUE due to payment failure")

    async def handle_payment_action_required(self, tenant_id: uuid.UUID) -> None:
        """Mark tenant as past_due when action is required (SCA)."""
        tenant = await self.db.get(Tenant, tenant_id)
        if tenant:
            tenant.status = TenantStatus.PAST_DUE
            await self.db.commit()
            logger.warning(f"Tenant {tenant_id} marked as PAST_DUE due to action required")

    async def handle_payment_succeeded(self, tenant_id: uuid.UUID) -> None:
        """Mark tenant as active when payment succeeds (recovery)."""
        tenant = await self.db.get(Tenant, tenant_id)
        if tenant:
            tenant.status = TenantStatus.ACTIVE
            await self.db.commit()
            logger.info(f"Tenant {tenant_id} marked as ACTIVE due to successful payment recovery")

    async def verify_webhook_signature(self, payload: bytes, sig_header: str) -> bool:
        """Verify Stripe webhook signature. Fails if secret is missing."""
        if not settings.stripe_webhook_secret:
            logger.critical("STRIPE_WEBHOOK_SECRET NOT SET. Refusing to process webhooks.")
            return False
            
        try:
            stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
            return True
        except Exception as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            return False

    async def check_live_readiness(self) -> Dict[str, Any]:
        """Final verification for live production billing."""
        return {
            "stripe_api_key_set": bool(settings.stripe_api_key),
            "webhook_secret_set": bool(settings.stripe_webhook_secret),
            "is_live_mode": settings.app_env == "production"
        }

    async def process_quota_transition(self, tenant_id: uuid.UUID) -> None:
        """Recalculate quotas or handle limits after a plan change."""
        # For now, quotas are calculated on-the-fly from tier
        pass

    async def track_billing_event(self, tenant_id: uuid.UUID, event_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Track billing-related events (e.g. invoice_created, payment_failed) for revenue analytics."""
        logger.info(
            "billing_event",
            tenant_id=str(tenant_id),
            event_type=event_type,
            metadata=metadata or {}
        )
        # Placeholder for recording to an Audit log or specialized revenue table

    async def scaffold_invoice_lifecycle(self, tenant_id: uuid.UUID, amount: float, status: str) -> None:
        """Scaffold for invoice generation and tracking."""
        logger.info(
            "invoice_lifecycle_scaffold",
            tenant_id=str(tenant_id),
            amount=amount,
            status=status
        )
        # Placeholder for future production invoicing logic
