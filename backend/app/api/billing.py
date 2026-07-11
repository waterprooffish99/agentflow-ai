import datetime as dt
import uuid
import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import func, select

from app.api import deps
from app.core.billing import get_plan
from app.core.config import settings
from app.core.redis import redis_client
from app.core.redis_keys import tenant_key
from app.models import Appointment, Customer, Tenant, TenantStatus
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])

logger = logging.getLogger(__name__)

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: deps.DBSession,
    stripe_signature: str = Header(None)
):
    """Handle Stripe webhooks for subscription and payment lifecycle."""
    if not settings.stripe_webhook_secret:
        logger.critical("STRIPE_WEBHOOK_SECRET is not configured. Failing closed.")
        raise HTTPException(
            status_code=500,
            detail="Stripe webhook secret is not configured"
        )

    payload = await request.body()
    service = BillingService(db)
    
    if not await service.verify_webhook_signature(payload, stripe_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    try:
        event = json.loads(payload)
        event_type = event.get("type")
        
        if event_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
            subscription = event["data"]["object"]
            metadata = subscription.get("metadata", {})
            tenant_id_str = metadata.get("tenant_id")
            
            if tenant_id_str:
                tenant_id = uuid.UUID(tenant_id_str)
                if event_type == "customer.subscription.deleted":
                    await service.handle_subscription_updated(
                        tenant_id, "free", new_status=TenantStatus.INACTIVE
                    )
                else:
                    new_tier = metadata.get("tier", "starter")
                    stripe_status = subscription.get("status")
                    if stripe_status in ["active", "trialing"]:
                        new_status = TenantStatus.ACTIVE
                    elif stripe_status == "past_due":
                        new_status = TenantStatus.PAST_DUE
                    else:
                        new_status = TenantStatus.INACTIVE
                        
                    await service.handle_subscription_updated(
                        tenant_id, 
                        new_tier, 
                        subscription.get("id"),
                        new_status=new_status
                    )
        
        elif event_type in ["invoice.payment_succeeded", "invoice.payment_failed", "invoice.payment_action_required"]:
            invoice = event["data"]["object"]
            # Tenant ID might be in metadata
            tenant_id_str = invoice.get("metadata", {}).get("tenant_id")
            
            if tenant_id_str:
                tenant_id = uuid.UUID(tenant_id_str)
                if event_type == "invoice.payment_succeeded":
                    await service.handle_payment_succeeded(tenant_id)
                elif event_type == "invoice.payment_failed":
                    await service.handle_payment_failed(tenant_id)
                else:
                    await service.handle_payment_action_required(tenant_id)
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/usage")
async def get_billing_usage(
    db: deps.DBSession,
    tenant_id: uuid.UUID = Depends(deps.get_tenant_id),
):
    """Get current plan and usage statistics for the tenant."""
    tenant = await db.get(Tenant, tenant_id)
    plan = get_plan(tenant.subscription_tier)

    # 1. AI Token Usage (from Redis)
    day = dt.date.today()
    month = dt.date(day.year, day.month, 1).isoformat()
    daily_key = tenant_key(tenant_id, "ai", "usage", day.isoformat())
    monthly_key = tenant_key(tenant_id, "ai", "usage", month)

    daily_tokens = await redis_client.hget(daily_key, "total_tokens")
    monthly_tokens = await redis_client.hget(monthly_key, "total_tokens")

    # 2. Booking Usage (from DB)
    month_start = dt.datetime(day.year, day.month, 1)
    bookings_count = await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.tenant_id == tenant_id, Appointment.created_at >= month_start
        )
    )

    # 3. Contact Usage (from DB)
    contacts_count = await db.execute(
        select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id)
    )

    return {
        "tier": tenant.subscription_tier,
        "plan": plan.model_dump(),
        "usage": {
            "ai_tokens": {
                "daily": int(daily_tokens) if daily_tokens else 0,
                "monthly": int(monthly_tokens) if monthly_tokens else 0,
                "daily_limit": plan.daily_tokens,
                "monthly_limit": plan.monthly_tokens,
            },
            "bookings": {
                "monthly": bookings_count.scalar() or 0,
                "monthly_limit": plan.monthly_bookings,
            },
            "contacts": {
                "total": contacts_count.scalar() or 0,
                "total_limit": plan.max_contacts,
            },
        },
    }
