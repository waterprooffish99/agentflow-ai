import pytest
import uuid
from app.services.onboarding_analytics_service import OnboardingAnalyticsService
from app.models import Tenant, BusinessProfile

@pytest.mark.asyncio
async def test_onboarding_stats(db_session):
    # Setup
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        business_name="Analytics Test",
        subscription_tier="free",
        status="active"
    )
    db_session.add(tenant)
    
    profile = BusinessProfile(
        tenant_id=tenant_id,
        description="Test business"
    )
    db_session.add(profile)
    await db_session.flush()
    
    service = OnboardingAnalyticsService(db_session)
    stats = await service.get_tenant_onboarding_stats(tenant_id)
    
    assert stats["setup"]["profile_complete"] is True
    assert stats["activation_score"] >= 10
    assert stats["is_activated"] is False # No conversations yet
