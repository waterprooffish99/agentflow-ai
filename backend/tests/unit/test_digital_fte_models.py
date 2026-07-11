import pytest
import uuid
from datetime import datetime, timezone
from app.models import Tenant, User, Conversation, Correction, PermissionPolicy, AutonomyLevel
from app.models.tenant import SubscriptionTier, TenantStatus
from app.models.user import UserRole, UserStatus
from app.models.conversation import ConversationStatus

@pytest.mark.asyncio
async def test_permission_policy_auto_seed(db_session):
    # Creating a tenant should trigger init listener and auto-seed PermissionPolicy
    tenant = Tenant(
        business_name="Auto Seed Test",
        subscription_tier=SubscriptionTier.FREE,
        status=TenantStatus.ACTIVE
    )
    db_session.add(tenant)
    await db_session.flush()

    assert tenant.autonomy_level == AutonomyLevel.MODE_1_SUPERVISED
    assert tenant.min_reviewed_conversations == 50
    assert tenant.max_correction_rate == 0.10
    
    assert tenant.permission_policy is not None
    assert tenant.permission_policy.tenant_id == tenant.id
    assert "answer_faq" in tenant.permission_policy.always_allowed_actions
    assert "discount_or_refund" in tenant.permission_policy.always_escalate_actions

@pytest.mark.asyncio
async def test_correction_creation_and_nullable_fields(db_session):
    # Setup Tenant
    tenant = Tenant(business_name="Correction Test")
    db_session.add(tenant)
    await db_session.flush()

    # Setup User
    user = User(
        tenant_id=tenant.id,
        email="reviewer@test.com",
        password_hash="test",
        role=UserRole.STAFF,
        status=UserStatus.ACTIVE,
        full_name="Reviewer User"
    )
    db_session.add(user)
    await db_session.flush()

    # Setup Conversation
    conversation = Conversation(
        tenant_id=tenant.id,
        status=ConversationStatus.ACTIVE
    )
    db_session.add(conversation)
    await db_session.flush()

    # Create Correction - was_edited = None (pending review), human_edited_message = None, reviewed_by = None
    correction = Correction(
        tenant_id=tenant.id,
        conversation_id=conversation.id,
        ai_draft_message="AI draft",
        was_edited=None
    )
    db_session.add(correction)
    await db_session.flush()

    assert correction.id is not None
    assert correction.tenant_id == tenant.id
    assert correction.conversation_id == conversation.id
    assert correction.ai_draft_message == "AI draft"
    assert correction.human_edited_message is None
    assert correction.was_edited is None
    assert correction.reviewed_by is None
    assert correction.reviewed_at is None

    # Review the Correction
    correction.was_edited = True
    correction.human_edited_message = "Human edit"
    correction.reviewed_by = user.id
    correction.reviewed_at = datetime.now(timezone.utc)
    await db_session.flush()

    assert correction.was_edited is True
    assert correction.human_edited_message == "Human edit"
    assert correction.reviewed_by == user.id


@pytest.mark.asyncio
async def test_correction_auto_logged_on_message(db_session):
    from app.services.ai_orchestrator_service import AIOrchestratorService
    from sqlalchemy import select

    # 1. Setup Tenant and Conversation
    tenant = Tenant(business_name="Auto Log Test Tenant")
    db_session.add(tenant)
    await db_session.flush()

    conversation = Conversation(
        tenant_id=tenant.id,
        status=ConversationStatus.ACTIVE
    )
    db_session.add(conversation)
    await db_session.flush()
    await db_session.commit()

    # 2. Call the handle_message orchestrator function
    orchestrator = AIOrchestratorService(db_session)
    result = await orchestrator.handle_message(
        conversation_id=conversation.id,
        tenant_id=tenant.id,
        content="Hello, is anyone there?"
    )

    assert result is not None
    assert "content" in result

    # 3. Query the Correction table to verify the draft was logged
    stmt = select(Correction).where(Correction.conversation_id == conversation.id)
    corrections_res = await db_session.execute(stmt)
    corrections = corrections_res.scalars().all()

    assert len(corrections) == 1
    assert corrections[0].ai_draft_message == result["content"]
    assert corrections[0].was_edited is None
    assert corrections[0].human_edited_message is None

