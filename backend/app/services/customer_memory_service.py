import uuid
from typing import Optional, Dict, Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer


class CustomerMemoryService:
    """Service for managing long-term memory and preferences for a customer."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_preferences(self, customer_id: uuid.UUID) -> Dict[str, Any]:
        """Fetch stored preferences for a customer."""
        result = await self.db.execute(
            select(Customer.preferences).where(Customer.id == customer_id)
        )
        prefs = result.scalar_one_or_none()
        return prefs or {}

    async def update_preferences(
        self, 
        customer_id: uuid.UUID, 
        new_prefs: Dict[str, Any]
    ):
        """Merge new preferences into existing customer profile."""
        current_prefs = await self.get_preferences(customer_id)
        current_prefs.update(new_prefs)
        
        await self.db.execute(
            update(Customer)
            .where(Customer.id == customer_id)
            .values(preferences=current_prefs)
        )
        await self.db.flush()

    async def get_customer_context(self, customer_id: uuid.UUID) -> str:
        """Format customer memory for AI context injection."""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            return ""

        context = f"Customer Name: {customer.name}\n"
        if customer.preferences:
            prefs_str = ", ".join([f"{k}: {v}" for k, v in customer.preferences.items()])
            context += f"Known Preferences: {prefs_str}\n"
        
        context += f"Total Bookings: {customer.total_bookings}\n"
        if customer.last_interaction_at:
            context += f"Last Interaction: {customer.last_interaction_at.strftime('%Y-%m-%d')}\n"
            
        return context
