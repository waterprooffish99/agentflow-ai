import enum
import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class LeadStatus(str, enum.Enum):
    UNQUALIFIED = "unqualified"
    PARTIALLY_QUALIFIED = "partially_qualified"
    QUALIFIED = "qualified"
    BOOKED = "booked"
    LOST = "lost"


class LeadUrgency(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Lead(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "leads"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[LeadStatus] = mapped_column(
        String(30), default=LeadStatus.UNQUALIFIED, nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    urgency: Mapped[LeadUrgency] = mapped_column(String(20), default=LeadUrgency.MEDIUM, nullable=False)
    budget_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_service: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_times: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)
    conversation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    qualifies_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer = relationship("Customer", back_populates="leads")
    conversations = relationship("Conversation", back_populates="lead", foreign_keys="Conversation.lead_id")
    appointments = relationship("Appointment", back_populates="lead")

    __table_args__ = (
        Index("ix_leads_tenant_status", "tenant_id", "status"),
        Index("ix_leads_tenant_created", "tenant_id", "created_at"),
        Index("ix_leads_assigned_to", "assigned_to"),
    )


class LeadCapture(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "lead_captures"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)
    field_value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    capture_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_lead_captures_lead", "lead_id"),
        Index("ix_lead_captures_conversation", "conversation_id"),
        Index("ix_lead_captures_tenant", "tenant_id"),
    )
