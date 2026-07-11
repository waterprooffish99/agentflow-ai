import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Lead, LeadPipelineStage, LeadStageHistory


class LeadPipelineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stages(self, tenant_id: uuid.UUID) -> List[LeadPipelineStage]:
        """Fetch all pipeline stages for a tenant ordered by position."""
        result = await self.db.execute(
            select(LeadPipelineStage)
            .where(LeadPipelineStage.tenant_id == tenant_id, LeadPipelineStage.is_active == True)
            .order_by(LeadPipelineStage.order.asc())
        )
        return result.scalars().all()

    async def move_lead_to_stage(
        self, 
        tenant_id: uuid.UUID, 
        lead_id: uuid.UUID, 
        stage_id: uuid.UUID
    ) -> bool:
        """Transition a lead to a new pipeline stage and record history."""
        # 1. Fetch stage name
        stage_res = await self.db.execute(select(LeadPipelineStage).where(LeadPipelineStage.id == stage_id))
        stage = stage_res.scalar_one_or_none()
        if not stage:
            return False

        # 2. Update the lead's current status
        await self.db.execute(
            update(Lead)
            .where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
            .values(status=stage.name)
        )
        
        # 3. Close the previous history entry
        now = datetime.now(timezone.utc)
        await self.db.execute(
            update(LeadStageHistory)
            .where(LeadStageHistory.lead_id == lead_id, LeadStageHistory.left_at == None)
            .values(left_at=now)
        )
        
        # 4. Create new history entry
        history = LeadStageHistory(
            tenant_id=tenant_id,
            lead_id=lead_id,
            stage_id=stage_id,
            entered_at=now
        )
        self.db.add(history)
        
        await self.db.flush()
        return True

    async def get_lead_history(self, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> List[LeadStageHistory]:
        """Fetch the movement history of a lead."""
        result = await self.db.execute(
            select(LeadStageHistory)
            .where(LeadStageHistory.lead_id == lead_id, LeadStageHistory.tenant_id == tenant_id)
            .order_by(LeadStageHistory.entered_at.desc())
        )
        return result.scalars().all()

    async def initialize_default_stages(self, tenant_id: uuid.UUID):
        """Seed default pipeline stages for a new tenant."""
        defaults = [
            {"name": "New Inquiry", "order": 0},
            {"name": "Qualified", "order": 1},
            {"name": "Meeting Scheduled", "order": 2},
            {"name": "Proposal Sent", "order": 3},
            {"name": "Closed Won", "order": 4, "is_winning": True},
            {"name": "Closed Lost", "order": 5, "is_losing": True},
        ]
        
        for d in defaults:
            stage = LeadPipelineStage(
                tenant_id=tenant_id,
                name=d["name"],
                order=d["order"],
                is_winning_stage=d.get("is_winning", False),
                is_losing_stage=d.get("is_losing", False)
            )
            self.db.add(stage)
        
        await self.db.flush()
