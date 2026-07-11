import uuid
import logging
from sqlalchemy import select
from app.models import PermissionPolicy, Conversation, ConversationStatus

logger = logging.getLogger(__name__)

NEG_SENTIMENT_KEYWORDS = {
    # English keywords
    "angry", "frustrated", "terrible", "bad service", "worst", "hate",
    "unhappy", "useless", "disappointed", "complaint", "manager", "representative",
    "human", "crap", "suck", "annoyed", "stupid",

    # Urdu Script keywords
    "خراب سروس", "بکار سروس", "فضول", "بکواس", "انسان سے بات", "نمائندے سے بات", 
    "مینیجر", "پیسہ واپس", "پیسے واپس", "اسکام", "دھوکہ", "فراڈ", "ریفنڈ",

    # Roman Urdu keywords
    "bekar service", "kharab service", "bakwas", "fazool", "insaan se baat", 
    "bande se baat", "manager se baat", "numainde se baat", "paisa wapis", 
    "paisa wapas", "peisa wapis", "peise wapis", "dhoka", "fraud", "refund", "scam"
}

def analyze_sentiment_is_negative(message_content: str) -> bool:
    """Basic keyword-based sentiment analysis for frustration/anger."""
    content_lower = message_content.lower()
    for kw in NEG_SENTIMENT_KEYWORDS:
        if kw in content_lower:
            return True
    return False

async def escalate_conversation(db, conversation_id: uuid.UUID, reason: str):
    """Update conversation status to escalated."""
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if conversation:
        conversation.status = ConversationStatus.ESCALATED
        conversation.escalated_reason = reason
        await db.flush()

async def check_action_permitted(
    db,
    tenant_id: uuid.UUID,
    conversation_id: uuid.UUID,
    action: str
) -> bool:
    """
    Check if a tool action is permitted under the tenant's policy.
    Returns True if allowed, False if it must escalate.
    """
    stmt = select(PermissionPolicy).where(PermissionPolicy.tenant_id == tenant_id)
    policy_res = await db.execute(stmt)
    policy = policy_res.scalar_one_or_none()

    if not policy:
        always_escalate = ["discount_or_refund", "cancellation", "negative_sentiment_detected", "outside_seeded_data"]
    else:
        always_escalate = policy.always_escalate_actions

    if action in always_escalate:
        logger.warning(f"Action '{action}' is in always_escalate list. Escalating.")
        await escalate_conversation(db, conversation_id, f"Action '{action}' requires authorization")
        return False

    return True
