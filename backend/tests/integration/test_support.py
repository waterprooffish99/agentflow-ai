import pytest
import uuid
from app.models import SupportIssue, SupportIssueType, Tenant, User, UserRole

@pytest.mark.asyncio
async def test_create_support_issue(db_session, client):
    # Setup: Need a Tenant and a User for foreign keys
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, business_name="Support Test")
    db_session.add(tenant)
    
    user_id = uuid.uuid4()
    user = User(
        id=user_id, 
        tenant_id=tenant_id, 
        email="test@test.com", 
        role=UserRole.BUSINESS_ADMIN, 
        password_hash="...",
        full_name="Test User"
    )
    db_session.add(user)
    
    await db_session.flush()
    
    issue = SupportIssue(
        tenant_id=tenant_id,
        user_id=user_id,
        issue_type=SupportIssueType.BUG,
        title="Integration Test Issue",
        description="Something is broken in the integration test"
    )
    db_session.add(issue)
    await db_session.flush()
    
    assert issue.id is not None
    assert issue.status == "open"
