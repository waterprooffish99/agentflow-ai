import enum
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class AppointmentStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Appointment(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Booked appointment slot."""

    __tablename__ = "appointments"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    staff_member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True
    )

    service_type: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        String(20), default=AppointmentStatus.CONFIRMED, nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cancellation fields
    cancelled_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    cancelled_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # For rescheduling: link to new appointment
    rescheduled_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )
    rescheduled_from_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    lead = relationship("Lead", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")
    staff_member = relationship("StaffMember", back_populates="appointments")

    __table_args__ = (
        Index("ix_appointments_tenant_start", "tenant_id", "start_time"),
        Index("ix_appointments_customer", "customer_id"),
        Index("ix_appointments_lead", "lead_id"),
    )