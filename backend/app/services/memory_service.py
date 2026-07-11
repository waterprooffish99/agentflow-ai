import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ConversationMemory


class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_memory(self, conversation_id: uuid.UUID) -> Optional[ConversationMemory]:
        """Fetch memory for a conversation."""
        result = await self.db.execute(
            select(ConversationMemory).where(ConversationMemory.conversation_id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def update_memory(
        self,
        conversation_id: uuid.UUID,
        tenant_id: uuid.UUID,
        summary: Optional[str] = None,
        facts: Optional[dict] = None,
        ai_state: Optional[dict] = None,
    ) -> ConversationMemory:
        """Create or update conversation memory."""
        memory = await self.get_memory(conversation_id)

        if not memory:
            memory = ConversationMemory(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                summary=summary,
                facts=facts or {},
                ai_state=ai_state or {},
            )
            self.db.add(memory)
        else:
            if summary:
                memory.summary = summary
            if facts:
                memory.facts.update(facts)
            if ai_state:
                memory.ai_state.update(ai_state)

        await self.db.flush()
        return memory
