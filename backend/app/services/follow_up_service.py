import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.idempotency import IdempotencyService
from app.models import FollowUpTask, FollowUpStatus


class FollowUpService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.idempotency = IdempotencyService(ttl_seconds=24 * 3600)

    async def create_task(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        title: str,
        due_at: datetime,
        description: Optional[str] = None,
        lead_id: Optional[uuid.UUID] = None,
        assigned_to: Optional[uuid.UUID] = None,
        is_automated: bool = False,
    ) -> FollowUpTask:
        """Schedule a follow-up reminder."""
        idem_payload = {
            "customer_id": str(customer_id),
            "title": title,
            "due_at": due_at.isoformat(),
            "lead_id": str(lead_id) if lead_id else None,
        }
        allowed = await self.idempotency.acquire(tenant_id, "followup.create", idem_payload)
        if not allowed:
            result = await self.db.execute(
                select(FollowUpTask).where(
                    FollowUpTask.tenant_id == tenant_id,
                    FollowUpTask.customer_id == customer_id,
                    FollowUpTask.title == title,
                    FollowUpTask.due_at == due_at,
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing
            raise ValueError("Duplicate follow-up scheduling blocked")

        task = FollowUpTask(
            tenant_id=tenant_id,
            customer_id=customer_id,
            lead_id=lead_id,
            assigned_to=assigned_to,
            title=title,
            description=description,
            due_at=due_at,
            status=FollowUpStatus.PENDING,
            is_automated=is_automated,
        )
        self.db.add(task)
        await self.db.flush()
        return task

    async def complete_task(
        self, 
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        notes: Optional[str] = None
    ) -> bool:
        """Mark a follow-up task as completed."""
        result = await self.db.execute(
            select(FollowUpTask).where(FollowUpTask.id == task_id, FollowUpTask.tenant_id == tenant_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            return False

        task.status = FollowUpStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        task.completion_notes = notes
        
        await self.db.flush()
        return True

    async def list_pending_tasks(
        self, 
        tenant_id: uuid.UUID, 
        user_id: Optional[uuid.UUID] = None
    ) -> List[FollowUpTask]:
        """List tasks that need attention."""
        query = select(FollowUpTask).where(
            FollowUpTask.tenant_id == tenant_id,
            FollowUpTask.status == FollowUpStatus.PENDING
        )
        if user_id:
            query = query.where(FollowUpTask.assigned_to == user_id)
        
        query = query.order_by(FollowUpTask.due_at.asc())
        result = await self.db.execute(query)
        return result.scalars().all()
