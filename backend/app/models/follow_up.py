import uuid
import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class FollowUpStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class FollowUpTask(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Reminder for staff to follow up with a customer."""
    __tablename__ = "follow_up_tasks"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[FollowUpStatus] = mapped_column(String(20), default=FollowUpStatus.PENDING, nullable=False)
    
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("Customer")
    lead = relationship("Lead")

    __table_args__ = (
        Index("ix_follow_up_tasks_tenant_due", "tenant_id", "due_at"),
        Index("ix_follow_up_tasks_customer", "customer_id"),
        Index("ix_follow_up_tasks_status", "status"),
    )
