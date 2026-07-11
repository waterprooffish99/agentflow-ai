import uuid
import pytest
from app.models import Tenant, Conversation, Correction, User, UserRole, UserStatus
from app.api.deps import get_current_user
from app.main import app

@pytest.mark.asyncio
async def test_corrections_api_flow(db_session, client):
    # 1. Setup mock tenant, user, conversation, correction
    tenant = Tenant(business_name="Corrections API Test Tenant")
    db_session.add(tenant)
    await db_session.flush()

    user = User(
        tenant_id=tenant.id,
        email="admin_corr@test.com",
        password_hash="test",
        role=UserRole.BUSINESS_ADMIN,
        full_name="Corr Admin User",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(
        tenant_id=tenant.id,
        status="active"
    )
    db_session.add(conversation)
    await db_session.flush()

    correction = Correction(
        tenant_id=tenant.id,
        conversation_id=conversation.id,
        ai_draft_message="Draft response to query",
        was_edited=None
    )
    db_session.add(correction)
    await db_session.flush()
    await db_session.commit()

    # 2. Mock auth dependency
    async def mock_current_user():
        return user
    app.dependency_overrides[get_current_user] = mock_current_user

    try:
        # 3. Test list pending corrections
        response = await client.get("/api/v1/corrections/pending")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(correction.id)
        assert data[0]["ai_draft_message"] == "Draft response to query"
        assert data[0]["was_edited"] is None

        # 4. Test review endpoint - was_edited = False (sent as-is)
        review_response = await client.post(
            f"/api/v1/corrections/{correction.id}/review",
            json={"was_edited": False}
        )
        assert review_response.status_code == 200
        review_data = review_response.json()
        assert review_data["was_edited"] is False
        assert review_data["human_edited_message"] is None
        assert review_data["reviewed_by"] == str(user.id)

        # 5. Check pending is now empty
        pending_response = await client.get("/api/v1/corrections/pending")
        assert pending_response.status_code == 200
        assert len(pending_response.json()) == 0

    finally:
        app.dependency_overrides.pop(get_current_user, None)
