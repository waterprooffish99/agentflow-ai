import pytest
import uuid
from app.services.billing_service import BillingService
from app.models import Tenant, SubscriptionTier, TenantStatus

@pytest.mark.asyncio
async def test_stripe_subscription_sync(db_session):
    # Setup
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Billing Test",
        subscription_tier=SubscriptionTier.FREE,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()
    
    billing_svc = BillingService(db_session)
    
    # Simulate a Stripe webhook update to Growth tier
    await billing_svc.handle_subscription_updated(
        tenant_id=tenant_id,
        new_tier="growth",
        stripe_subscription_id="sub_12345",
        new_status=TenantStatus.ACTIVE
    )
    
    await db_session.refresh(tenant)
    assert tenant.subscription_tier == SubscriptionTier.GROWTH
    assert tenant.settings["stripe_subscription_id"] == "sub_12345"
    assert tenant.status == TenantStatus.ACTIVE

@pytest.mark.asyncio
async def test_handle_payment_failure(db_session):
    # Setup active tenant
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Failure Test",
        subscription_tier=SubscriptionTier.STARTER,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()
    
    billing_svc = BillingService(db_session)
    
    # Simulate payment failure
    await billing_svc.handle_payment_failed(tenant_id)
    
    await db_session.refresh(tenant)
    assert tenant.status == TenantStatus.PAST_DUE

@pytest.mark.asyncio
async def test_handle_subscription_deleted(db_session):
    # Setup active tenant
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Cancellation Test",
        subscription_tier=SubscriptionTier.GROWTH,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()
    
    billing_svc = BillingService(db_session)
    
    # Simulate subscription deletion (cancellation)
    await billing_svc.handle_subscription_updated(
        tenant_id=tenant_id,
        new_tier="free",
        new_status=TenantStatus.INACTIVE
    )
    
    await db_session.refresh(tenant)
    assert tenant.status == TenantStatus.INACTIVE
    assert tenant.subscription_tier == SubscriptionTier.FREE
