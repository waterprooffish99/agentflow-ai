import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TenantMixin, UUIDMixin

class Correction(Base, UUIDMixin, TenantMixin):
    """Training and proof record for supervised Mode 1 replies."""
    __tablename__ = "corrections"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    ai_draft_message: Mapped[str] = mapped_column(Text, nullable=False)
    human_edited_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    was_edited: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    conversation = relationship("Conversation")
    reviewer = relationship("User")

    __table_args__ = (
        Index("ix_corrections_conversation", "conversation_id"),
        Index("ix_corrections_tenant", "tenant_id"),
    )
