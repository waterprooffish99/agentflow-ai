import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FAQEntry


class FAQRetrievalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_faqs(self, tenant_id: uuid.UUID) -> List[FAQEntry]:
        """Fetch all active FAQ entries for a tenant to inject into AI context."""
        result = await self.db.execute(
            select(FAQEntry).where(
                FAQEntry.tenant_id == tenant_id,
                FAQEntry.is_active == True
            )
        )
        return result.scalars().all()

    async def search_faqs(self, tenant_id: uuid.UUID, query: str) -> List[FAQEntry]:
        """Simple string search for relevant FAQs (placeholder for RAG)."""
        # For MVP, we search in question/answer fields
        result = await self.db.execute(
            select(FAQEntry).where(
                FAQEntry.tenant_id == tenant_id,
                FAQEntry.is_active == True,
                (FAQEntry.question.ilike(f"%{query}%")) | (FAQEntry.answer.ilike(f"%{query}%"))
            ).limit(5)
        )
        return result.scalars().all()
