import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, String, Text, ForeignKey, Index, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin

class ExperimentStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class Experiment(Base, UUIDMixin, TimestampMixin):
    """Growth experimentation infrastructure."""
    __tablename__ = "experiments"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ExperimentStatus] = mapped_column(String(20), default=ExperimentStatus.DRAFT, nullable=False)
    
    # Targeting
    target_percentage: Mapped[int] = mapped_column(default=0, nullable=False)
    target_tiers: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)
    
    # Variants (e.g. {"A": {"prompt_v": 1}, "B": {"prompt_v": 2}})
    variants: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    start_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class TenantExperimentAssignment(Base, UUIDMixin, TimestampMixin):
    """Tracking which variant a tenant was assigned to."""
    __tablename__ = "tenant_experiment_assignments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    experiment_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_tenant_experiment_assignment", "tenant_id", "experiment_name", unique=True),
    )
