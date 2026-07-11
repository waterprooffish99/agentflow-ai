import pytest
import uuid
import json
from app.core.config import settings
from app.models import Tenant, TenantStatus, SubscriptionTier, User, UserRole
from app.services.billing_service import BillingService
from app.api.deps import get_current_user
from app.main import app


@pytest.mark.asyncio
async def test_stripe_webhook_no_secret(client, monkeypatch):
    """Webhook fails closed (500) if Stripe webhook secret is not configured."""
    monkeypatch.setattr(settings, "stripe_webhook_secret", None)
    
    response = await client.post(
        "/api/v1/billing/webhooks/stripe",
        content=b"{}",
        headers={"Stripe-Signature": "t=123,v1=sig"}
    )
    
    assert response.status_code == 500
    assert "Stripe webhook secret is not configured" in response.json()["detail"]


@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature(client, monkeypatch):
    """Webhook returns 400 if secret is configured but signature verification fails."""
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    
    # Force verify_webhook_signature to return False to simulate verification failure
    async def mock_verify(*args, **kwargs):
        return False
    monkeypatch.setattr(BillingService, "verify_webhook_signature", mock_verify)
    
    response = await client.post(
        "/api/v1/billing/webhooks/stripe",
        content=b"{}",
        headers={"Stripe-Signature": "invalid-signature"}
    )
    
    assert response.status_code == 400
    assert "Invalid signature" in response.json()["detail"]


@pytest.mark.asyncio
async def test_tenant_status_middleware_active_tenant(db_session, client):
    """Active tenant can access non-billing POST endpoints normally."""
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Active Business",
        subscription_tier=SubscriptionTier.STARTER,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/start",
        json={"tenant_id": str(tenant_id), "customer_id": None},
        headers={"X-API-Key": "test-key"}
    )
    # Status should NOT be 402 Payment Required. (It will be 200 or 400/500 if external APIs are missing, but not 402)
    assert response.status_code != 402


@pytest.mark.asyncio
async def test_tenant_status_middleware_past_due_tenant(db_session, client):
    """Past due tenant is restricted: allowed GET (read-only), but blocked POST/chat (402)."""
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Past Due Business",
        subscription_tier=SubscriptionTier.STARTER,
        status=TenantStatus.PAST_DUE
    )
    db_session.add(tenant)
    
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="test_past_due@test.com",
        role=UserRole.BUSINESS_ADMIN,
        password_hash="...",
        full_name="Test User",
        status="active"
    )
    db_session.add(user)
    await db_session.flush()

    # Override get_current_user dependency to return our test user
    async def mock_current_user():
        return user
    app.dependency_overrides[get_current_user] = mock_current_user

    try:
        # 1. POST to chat (orchestration/writes) -> blocked with 402
        response = await client.post(
            "/api/v1/chat/start",
            json={"tenant_id": str(tenant_id), "customer_id": None},
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == 402
        assert "Payment is past due" in response.json()["error"]["message"]

        # 2. GET to billing/usage (billing route) -> allowed
        response = await client.get(
            "/api/v1/billing/usage",
            headers={"X-Tenant-ID": str(tenant_id)}
        )
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_tenant_status_middleware_inactive_tenant(db_session, client):
    """Inactive tenant is blocked (402) on all non-billing routes including chat & reads."""
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Inactive Business",
        subscription_tier=SubscriptionTier.FREE,
        status=TenantStatus.INACTIVE
    )
    db_session.add(tenant)
    
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="test_inactive@test.com",
        role=UserRole.BUSINESS_ADMIN,
        password_hash="...",
        full_name="Test User",
        status="active"
    )
    db_session.add(user)
    await db_session.flush()

    # Override get_current_user dependency to return our test user
    async def mock_current_user():
        return user
    app.dependency_overrides[get_current_user] = mock_current_user

    try:
        # 1. POST to chat -> blocked with 402
        response = await client.post(
            "/api/v1/chat/start",
            json={"tenant_id": str(tenant_id), "customer_id": None},
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == 402
        assert "Tenant subscription is inactive" in response.json()["error"]["message"]

        # 2. GET to billing/usage (billing route) -> allowed
        response = await client.get(
            "/api/v1/billing/usage",
            headers={"X-Tenant-ID": str(tenant_id)}
        )
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_stripe_webhook_payment_transitions(db_session, client, monkeypatch):
    """Webhook correctly transitions tenant status on various events."""
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    
    async def mock_verify(*args, **kwargs):
        return True
    monkeypatch.setattr(BillingService, "verify_webhook_signature", mock_verify)

    # Setup Tenant
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Webhook Transition Business",
        subscription_tier=SubscriptionTier.STARTER,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()

    # 1. invoice.payment_failed -> PAST_DUE
    payload_failed = {
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "metadata": {
                    "tenant_id": str(tenant_id)
                }
            }
        }
    }
    response = await client.post(
        "/api/v1/billing/webhooks/stripe",
        json=payload_failed,
        headers={"Stripe-Signature": "valid-signature"}
    )
    assert response.status_code == 200
    await db_session.refresh(tenant)
    assert tenant.status == TenantStatus.PAST_DUE

    # 2. invoice.payment_succeeded -> ACTIVE
    payload_success = {
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "metadata": {
                    "tenant_id": str(tenant_id)
                }
            }
        }
    }
    response = await client.post(
        "/api/v1/billing/webhooks/stripe",
        json=payload_success,
        headers={"Stripe-Signature": "valid-signature"}
    )
    assert response.status_code == 200
    await db_session.refresh(tenant)
    assert tenant.status == TenantStatus.ACTIVE

    # 3. customer.subscription.deleted -> INACTIVE
    payload_deleted = {
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "metadata": {
                    "tenant_id": str(tenant_id)
                }
            }
        }
    }
    response = await client.post(
        "/api/v1/billing/webhooks/stripe",
        json=payload_deleted,
        headers={"Stripe-Signature": "valid-signature"}
    )
    assert response.status_code == 200
    await db_session.refresh(tenant)
    assert tenant.status == TenantStatus.INACTIVE
    assert tenant.subscription_tier == SubscriptionTier.FREE

    # 4. customer.subscription.updated (status: past_due) -> PAST_DUE
    payload_updated_past_due = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_updated_123",
                "status": "past_due",
                "metadata": {
                    "tenant_id": str(tenant_id),
                    "tier": "starter"
                }
            }
        }
    }
    response = await client.post(
        "/api/v1/billing/webhooks/stripe",
        json=payload_updated_past_due,
        headers={"Stripe-Signature": "valid-signature"}
    )
    assert response.status_code == 200
    await db_session.refresh(tenant)
    assert tenant.status == TenantStatus.PAST_DUE
    assert tenant.subscription_tier == SubscriptionTier.STARTER
