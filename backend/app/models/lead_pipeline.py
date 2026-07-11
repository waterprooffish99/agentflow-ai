import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class LeadPipelineStage(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "lead_pipeline_stages"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_winning_stage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_losing_stage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (Index("ix_lead_pipeline_stages_tenant_order", "tenant_id", "order"),)


class LeadStageHistory(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "lead_stage_history"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lead_pipeline_stages.id", ondelete="CASCADE"), nullable=False
    )
    entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_lead_stage_history_lead", "lead_id"),
        Index("ix_lead_stage_history_tenant", "tenant_id"),
    )
