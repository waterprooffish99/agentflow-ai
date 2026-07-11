import enum
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Sent notification record."""

    __tablename__ = "notifications"

    recipient_type: Mapped[str] = mapped_column(String(20), nullable=False)  # customer, staff, admin
    recipient_address: Mapped[str] = mapped_column(String(255), nullable=False)  # email or phone
    channel: Mapped[NotificationChannel] = mapped_column(String(20), nullable=False)
    template: Mapped[str] = mapped_column(String(100), nullable=False)
    context: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        String(20), default=NotificationStatus.PENDING, nullable=False, index=True
    )
    sent_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_notifications_tenant_status", "tenant_id", "status"),
        Index("ix_notifications_tenant_channel", "tenant_id", "channel"),
    )