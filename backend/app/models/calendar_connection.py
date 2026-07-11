import uuid
import enum
from sqlalchemy import String, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class CalendarProvider(str, enum.Enum):
    GOOGLE = "google"
    OUTLOOK = "outlook"
    INTERNAL = "internal"

class CalendarConnection(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Connection to an external calendar provider."""
    __tablename__ = "calendar_connections"

    staff_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff_members.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[CalendarProvider] = mapped_column(String(20), nullable=False)
    external_calendar_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # OAuth tokens and refresh tokens
    credentials: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
