import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional, Any

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Customer, CustomerNote, CustomerTag, CustomerActivity

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_customer(self, customer_id: uuid.UUID) -> Optional[Customer]:
        """Fetch customer with tags and notes."""
        result = await self.db.execute(
            select(Customer)
            .where(Customer.id == customer_id)
            .options(
                selectinload(Customer.tags),
                selectinload(Customer.notes)
            )
        )
        return result.scalar_one_or_none()

    async def list_customers(
        self, 
        tenant_id: uuid.UUID, 
        limit: int = 50, 
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[Customer]:
        """List customers for a tenant with optional search."""
        query = select(Customer).where(Customer.tenant_id == tenant_id)
        
        if search:
            query = query.where(
                (Customer.name.ilike(f"%{search}%")) | 
                (Customer.email.ilike(f"%{search}%")) | 
                (Customer.phone.ilike(f"%{search}%"))
            )
            
        query = query.order_by(Customer.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_note(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        content: str,
        author_id: Optional[uuid.UUID] = None,
        is_ai: bool = False
    ) -> CustomerNote:
        """Create a new note for a customer."""
        note = CustomerNote(
            tenant_id=tenant_id,
            customer_id=customer_id,
            content=content,
            author_id=author_id,
            is_ai_generated=is_ai
        )
        self.db.add(note)
        
        # Log activity
        await ActivityTimelineService(self.db).log_activity(
            tenant_id=tenant_id,
            customer_id=customer_id,
            activity_type="note",
            description=f"{'AI' if is_ai else 'Staff'} added a note",
            reference_id=note.id,
            reference_type="customer_note"
        )
        
        await self.db.flush()
        return note

class ActivityTimelineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_activity(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        activity_type: str,
        description: str,
        reference_id: Optional[uuid.UUID] = None,
        reference_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> CustomerActivity:
        """Log an event in the customer's timeline."""
        activity = CustomerActivity(
            tenant_id=tenant_id,
            customer_id=customer_id,
            activity_type=activity_type,
            description=description,
            reference_id=reference_id,
            reference_type=reference_type,
            metadata_json=metadata or {}
        )
        self.db.add(activity)
        
        # Update customer last interaction
        await self.db.execute(
            update(Customer)
            .where(Customer.id == customer_id)
            .values(last_interaction_at=datetime.now(timezone.utc))
        )
        
        await self.db.flush()
        return activity

    async def get_timeline(
        self, 
        customer_id: uuid.UUID, 
        limit: int = 50
    ) -> List[CustomerActivity]:
        """Fetch activity history for a customer."""
        result = await self.db.execute(
            select(CustomerActivity)
            .where(CustomerActivity.customer_id == customer_id)
            .order_by(CustomerActivity.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
