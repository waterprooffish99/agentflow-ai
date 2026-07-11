import uuid
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Lead, LeadStatus, LeadCapture


class LeadQualificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_lead(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        conversation_id: uuid.UUID,
    ) -> Lead:
        """Find an existing active lead or create a new one for the conversation."""
        result = await self.db.execute(
            select(Lead).where(
                Lead.customer_id == customer_id,
                Lead.status.in_([LeadStatus.UNQUALIFIED, LeadStatus.PARTIALLY_QUALIFIED])
            ).limit(1)
        )
        lead = result.scalar_one_or_none()

        if not lead:
            lead = Lead(
                tenant_id=tenant_id,
                customer_id=customer_id,
                conversation_id=conversation_id,
                status=LeadStatus.UNQUALIFIED,
            )
            self.db.add(lead)
            await self.db.flush()
        
        return lead

    async def capture_field(
        self,
        tenant_id: uuid.UUID,
        lead_id: uuid.UUID,
        conversation_id: uuid.UUID,
        field_name: str,
        field_value: str,
        confidence: Optional[float] = None,
        metadata: Optional[dict] = None,
    ) -> LeadCapture:
        """Record a specific piece of information captured from the customer."""
        capture = LeadCapture(
            tenant_id=tenant_id,
            lead_id=lead_id,
            conversation_id=conversation_id,
            field_name=field_name,
            field_value=field_value,
            confidence_score=confidence,
            capture_metadata=metadata,
        )
        self.db.add(capture)
        
        # Also update the lead status if it was unqualified
        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if lead and lead.status == LeadStatus.UNQUALIFIED:
            lead.status = LeadStatus.PARTIALLY_QUALIFIED
        
        await self.db.flush()
        return capture

    async def list_captures(self, lead_id: uuid.UUID) -> List[LeadCapture]:
        """List all data points captured for a lead."""
        result = await self.db.execute(
            select(LeadCapture).where(LeadCapture.lead_id == lead_id)
        )
        return result.scalars().all()
