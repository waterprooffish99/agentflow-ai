import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    BUSINESS_ADMIN = "business_admin"
    STAFF = "staff"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(Base, UUIDMixin, TimestampMixin):
    """Platform user (admin, staff, or super admin)."""

    __tablename__ = "users"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[UserStatus] = mapped_column(String(20), default=UserStatus.ACTIVE, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Verification and reset tokens (stored as hash)
    email_verify_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")

    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_tenant_role", "tenant_id", "role"),
    )