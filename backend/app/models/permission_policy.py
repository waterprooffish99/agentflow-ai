import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin

class PermissionPolicy(Base, UUIDMixin, TimestampMixin):
    """Tenant permission policies config mapping always-allowed actions vs human-required escalations."""
    __tablename__ = "permission_policies"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    always_allowed_actions: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    always_escalate_actions: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    tenant = relationship("Tenant", back_populates="permission_policy")
