import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    INACTIVE = "inactive"


class AutonomyLevel(str, enum.Enum):
    MODE_1_SUPERVISED = "mode_1_supervised"
    MODE_2_AUTONOMOUS = "mode_2_autonomous"


class Tenant(Base, UUIDMixin, TimestampMixin):
    """Business tenant account."""

    __tablename__ = "tenants"

    business_name: Mapped[str] = mapped_column(String(100), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        String(20), default=SubscriptionTier.FREE, nullable=False
    )
    status: Mapped[TenantStatus] = mapped_column(
        String(20), default=TenantStatus.TRIAL, nullable=False
    )
    
    # Autonomy Config
    autonomy_level: Mapped[AutonomyLevel] = mapped_column(
        String(30), default=AutonomyLevel.MODE_1_SUPERVISED, nullable=False
    )
    min_reviewed_conversations: Mapped[int] = mapped_column(default=50, nullable=False)
    max_correction_rate: Mapped[float] = mapped_column(default=0.10, nullable=False)

    # Lead Attribution
    lead_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    campaign_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    referral_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    acquisition_channel: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Lifecycle Tracking
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # JSONB for flexible per-tenant settings: hours, services, staff, AI config
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ai_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship("app.models.user.User", back_populates="tenant", cascade="all, delete-orphan")
    permission_policy = relationship(
        "PermissionPolicy",
        back_populates="tenant",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_tenants_business_name", "business_name", unique=True),
        Index("ix_tenants_status", "status"),
        Index("ix_tenants_lead_source", "lead_source"),
        Index("ix_tenants_acquisition_channel", "acquisition_channel"),
    )


@event.listens_for(Tenant, "init")
def receive_init(target, args, kwargs):
    if "permission_policy" not in kwargs:
        from app.models.permission_policy import PermissionPolicy
        target.permission_policy = PermissionPolicy(
            always_allowed_actions=["answer_faq", "quote_price", "check_availability", "capture_lead", "propose_slot"],
            always_escalate_actions=["discount_or_refund", "cancellation", "negative_sentiment_detected", "outside_seeded_data"]
        )