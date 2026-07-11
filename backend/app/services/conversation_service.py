import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation, ConversationStatus, Message, MessageRole


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self,
        tenant_id: uuid.UUID,
        customer_id: Optional[uuid.UUID] = None,
        lead_id: Optional[uuid.UUID] = None,
    ) -> Conversation:
        """Initialize a new AI conversation."""
        conversation = Conversation(
            tenant_id=tenant_id,
            customer_id=customer_id,
            lead_id=lead_id,
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def get_conversation(
        self, conversation_id: uuid.UUID, tenant_id: Optional[uuid.UUID] = None
    ) -> Optional[Conversation]:
        """Fetch a conversation with its messages."""
        filters = [Conversation.id == conversation_id]
        if tenant_id:
            filters.append(Conversation.tenant_id == tenant_id)
        result = await self.db.execute(
            select(Conversation)
            .where(*filters)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        tenant_id: uuid.UUID,
        role: MessageRole,
        content: str,
        metadata: Optional[dict] = None,
    ) -> Message:
        """Add a new message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            role=role,
            content=content,
            metadata_json=metadata,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def list_messages(self, conversation_id: uuid.UUID, tenant_id: uuid.UUID) -> List[Message]:
        """Get all messages for a conversation, ordered by creation."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.tenant_id == tenant_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()

    async def close_conversation(self, conversation_id: uuid.UUID, tenant_id: uuid.UUID):
        """Mark a conversation as closed."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id, Conversation.tenant_id == tenant_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.status = ConversationStatus.CLOSED
            conversation.ended_at = datetime.now(timezone.utc)
            await self.db.flush()
