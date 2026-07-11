import pytest
import uuid
from app.core.billing import PLANS, SubscriptionTier
from app.services.quota_service import QuotaEnforcerService
from app.models import Tenant

@pytest.mark.asyncio
async def test_quota_enforcement_free_tier(db_session):
    # Setup a free tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        business_name="Free Test",
        subscription_tier=SubscriptionTier.FREE,
        status="active"
    )
    db_session.add(tenant)
    await db_session.flush()
    
    quota_service = QuotaEnforcerService(db_session)
    
    # FREE tier has 10 monthly bookings
    # For now, it should return True because we have 0 bookings
    assert await quota_service.can_add_booking(tenant.id) is True
    
    # Feature check
    assert await quota_service.has_feature(tenant.id, "basic_chat") is True
    assert await quota_service.has_feature(tenant.id, "analytics") is False
