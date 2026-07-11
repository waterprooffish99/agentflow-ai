import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class Customer(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """End customer of a business (lead source)."""

    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # AI/CRM metadata
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    total_bookings: Mapped[int] = mapped_column(default=0, nullable=False)
    last_interaction_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    leads = relationship("Lead", back_populates="customer")
    appointments = relationship("Appointment", back_populates="customer")
    notes = relationship("CustomerNote", back_populates="customer", cascade="all, delete-orphan")
    tags = relationship("CustomerTag", secondary="customer_tag_links", back_populates="customers")
    activities = relationship("CustomerActivity", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_customers_tenant_email", "tenant_id", "email", unique=True, postgresql_where=email.isnot(None)),
        Index("ix_customers_tenant_phone", "tenant_id", "phone", unique=True, postgresql_where=phone.isnot(None)),
    )


class CustomerNote(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Internal or AI-generated notes about a customer."""

    __tablename__ = "customer_notes"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_ai_generated: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="notes")

    __table_args__ = (
        Index("ix_customer_notes_customer", "customer_id"),
        Index("ix_customer_notes_tenant", "tenant_id"),
    )


class CustomerTag(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Custom tags for customer segmentation."""

    __tablename__ = "customer_tags"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True) # Hex code

    # Relationships
    customers = relationship("Customer", secondary="customer_tag_links", back_populates="tags")

    __table_args__ = (
        Index("ix_customer_tags_tenant_name", "tenant_id", "name", unique=True),
    )


class CustomerTagLink(Base, TenantMixin):
    """Many-to-many link between customers and tags."""

    __tablename__ = "customer_tag_links"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customer_tags.id", ondelete="CASCADE"), primary_key=True
    )


class CustomerActivity(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Timeline of customer interactions (bookings, chats, status changes)."""

    __tablename__ = "customer_activities"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False) # chat, booking, note, lead_status
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Reference to the actual entity (optional)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="activities")

    __table_args__ = (
        Index("ix_customer_activities_customer", "customer_id"),
        Index("ix_customer_activities_tenant", "tenant_id"),
    )
