import uuid
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class StaffMember(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Staff member within a tenant business."""
    __tablename__ = "staff_members"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    availability_rules = relationship("AvailabilityRule", back_populates="staff_member")
    appointments = relationship("Appointment", back_populates="staff_member")
