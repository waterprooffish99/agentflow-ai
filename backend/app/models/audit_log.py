import uuid

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, UUIDMixin


class AuditLog(Base, UUIDMixin, TenantMixin):
    """System activity log for compliance."""

    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # "lead.updated", "appointment.created"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "lead", "appointment", "user"
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # {"old": {...}, "new": {...}}
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 compatible
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_audit_tenant_timestamp", "tenant_id", "timestamp"),
    )