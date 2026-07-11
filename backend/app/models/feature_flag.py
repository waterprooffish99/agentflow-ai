import enum
import uuid
from typing import List, Optional

from sqlalchemy import Boolean, Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin

class FeatureStatus(str, enum.Enum):
    DISABLED = "disabled"
    BETA = "beta"
    STAGED = "staged"
    ENABLED = "enabled"

class FeatureFlag(Base, UUIDMixin, TimestampMixin):
    """Global feature flags for staged rollouts."""
    __tablename__ = "feature_flags"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. "new_analytics_v2"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[FeatureStatus] = mapped_column(String(20), default=FeatureStatus.DISABLED, nullable=False)
    
    # Rollout rules (e.g. percentage of tenants, specific tiers)
    rollout_percentage: Mapped[int] = mapped_column(default=0, nullable=False)
    allowed_tiers: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False) # ["growth", "enterprise"]
    
    is_global: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class TenantFeatureOverride(Base, UUIDMixin, TimestampMixin):
    """Tenant-specific feature flag overrides."""
    __tablename__ = "tenant_feature_overrides"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_tenant_feature_override", "tenant_id", "feature_name", unique=True),
    )
