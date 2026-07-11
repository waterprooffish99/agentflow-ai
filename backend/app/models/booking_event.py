import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class BookingEvent(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Audit log for booking-related activities."""
    __tablename__ = "booking_events"

    appointment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False
    )
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. created, cancelled, rescheduled
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False) # e.g. ai, user, customer
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
