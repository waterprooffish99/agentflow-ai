import pytest
import uuid
from app.models import Tenant, Conversation, PermissionPolicy, ConversationStatus
from app.models.tenant import SubscriptionTier, TenantStatus
from app.agents.escalation import check_action_permitted, analyze_sentiment_is_negative
from app.services.ai_orchestrator_service import AIOrchestratorService

@pytest.mark.asyncio
async def test_sentiment_analysis_frustration():
    assert analyze_sentiment_is_negative("I am so angry, this is terrible service!") is True
    assert analyze_sentiment_is_negative("please cancel my booking immediately") is False
    assert analyze_sentiment_is_negative("Hello, can you help me check if Saturday is open?") is False
    assert analyze_sentiment_is_negative("یہ بہت خراب سروس ہے، مجھے انسان سے بات کرنی ہے") is True
    assert analyze_sentiment_is_negative("yeh bohat bekar service hai, mujhe insaan se baat karni hai") is True
    assert analyze_sentiment_is_negative("bhai yeh scam lag raha hai mujhe paisa wapis chahiye") is True

@pytest.mark.asyncio
async def test_permission_budget_action_allowed(db_session):
    # Setup Tenant with standard defaults
    tenant = Tenant(business_name="Allowed Action Tenant")
    db_session.add(tenant)
    await db_session.flush()

    conversation = Conversation(tenant_id=tenant.id, status=ConversationStatus.ACTIVE)
    db_session.add(conversation)
    await db_session.flush()

    # check_availability is allowed by default
    permitted = await check_action_permitted(db_session, tenant.id, conversation.id, "check_availability")
    assert permitted is True
    
    # Reload conversation and verify status remains ACTIVE
    await db_session.refresh(conversation)
    assert conversation.status == ConversationStatus.ACTIVE

@pytest.mark.asyncio
async def test_permission_budget_action_escalated(db_session):
    # Setup Tenant with custom policy
    tenant = Tenant(business_name="Escalated Action Tenant")
    db_session.add(tenant)
    await db_session.flush()

    # Custom Permission Policy (modifying the auto-seeded policy)
    tenant.permission_policy.always_allowed_actions = ["quote_price"]
    tenant.permission_policy.always_escalate_actions = ["custom_dangerous_action"]
    await db_session.flush()

    conversation = Conversation(tenant_id=tenant.id, status=ConversationStatus.ACTIVE)
    db_session.add(conversation)
    await db_session.flush()

    # custom_dangerous_action should escalate
    permitted = await check_action_permitted(db_session, tenant.id, conversation.id, "custom_dangerous_action")
    assert permitted is False

    # Verify conversation status is now ESCALATED
    await db_session.refresh(conversation)
    assert conversation.status == ConversationStatus.ESCALATED
    assert "custom_dangerous_action" in conversation.escalated_reason

@pytest.mark.asyncio
async def test_orchestrator_intercepts_negative_sentiment(db_session):
    # Setup Tenant and Conversation
    tenant = Tenant(business_name="Sentiment Intercept Tenant")
    db_session.add(tenant)
    await db_session.flush()

    conversation = Conversation(tenant_id=tenant.id, status=ConversationStatus.ACTIVE)
    db_session.add(conversation)
    await db_session.flush()
    await db_session.commit()

    orchestrator = AIOrchestratorService(db_session)
    result = await orchestrator.handle_message(
        conversation_id=conversation.id,
        tenant_id=tenant.id,
        content="This is terrible service, I want to talk to a human manager right now!"
    )

    assert "escalating" in result["content"].lower()

    # Verify conversation is escalated in DB
    await db_session.refresh(conversation)
    assert conversation.status == ConversationStatus.ESCALATED
    assert conversation.escalated_reason == "Negative sentiment detected"
