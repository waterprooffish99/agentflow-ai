import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class AvailabilityException(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Specific dates/times where regular availability is overridden."""
    __tablename__ = "availability_exceptions"

    staff_member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff_members.id", ondelete="CASCADE"), nullable=True
    )
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # If False, the staff is NOT available during this period (e.g. vacation)
    # If True, the staff IS available (e.g. special working hours)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
