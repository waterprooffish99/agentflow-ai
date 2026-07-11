import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    ESCALATED = "escalated"
    CLOSED = "closed"


class Conversation(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "conversations"

    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=True
    )
    status: Mapped[ConversationStatus] = mapped_column(
        String(20), default=ConversationStatus.ACTIVE, nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    escalated_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    escalated_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lead = relationship("Lead", back_populates="conversations", foreign_keys=[lead_id])
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    memory = relationship("ConversationMemory", back_populates="conversation", uselist=False)

    __table_args__ = (
        Index("ix_conversations_lead", "lead_id"),
        Index("ix_conversations_tenant_status", "tenant_id", "status"),
    )


class MessageRole(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", type_=JSONB, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation", "conversation_id"),
        Index("ix_messages_tenant", "tenant_id"),
    )


class ConversationMemory(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "conversation_memory"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    facts: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ai_state: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    conversation = relationship("Conversation", back_populates="memory")

    __table_args__ = (
        Index("ix_conversation_memory_conversation", "conversation_id"),
        Index("ix_conversation_memory_tenant", "tenant_id"),
    )
