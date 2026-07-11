import uuid
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Tuple, Optional

class CalendarProviderBase(ABC):
    """Abstract interface for calendar operations."""
    
    @abstractmethod
    async def get_free_busy(
        self, 
        tenant_id: uuid.UUID, 
        start_date: date, 
        end_date: date,
        staff_member_id: Optional[uuid.UUID] = None
    ) -> List[Tuple[datetime, datetime]]:
        """Fetch busy time slots from the provider."""
        pass

    @abstractmethod
    async def create_event(
        self, 
        tenant_id: uuid.UUID, 
        title: str, 
        start_time: datetime, 
        end_time: datetime,
        staff_member_id: Optional[uuid.UUID] = None
    ) -> str:
        """Create an event in the calendar and return provider ID."""
        pass

    @abstractmethod
    async def delete_event(
        self, 
        tenant_id: uuid.UUID, 
        event_id: str,
        staff_member_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Delete an event from the calendar."""
        pass
