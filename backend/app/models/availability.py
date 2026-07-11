import enum
import uuid
from sqlalchemy import String, Time, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class AvailabilityRule(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Recurring availability rules for a business."""
    __tablename__ = "availability_rules"

    staff_member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff_members.id", ondelete="CASCADE"), nullable=True
    )

    day_of_week: Mapped[DayOfWeek] = mapped_column(String(20), nullable=False)
    start_time: Mapped[str] = mapped_column(Time, nullable=False)
    end_time: Mapped[str] = mapped_column(Time, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    staff_member = relationship("StaffMember", back_populates="availability_rules")
