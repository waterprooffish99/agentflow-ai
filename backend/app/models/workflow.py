import enum
import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class WorkflowTrigger(str, enum.Enum):
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    LEAD_COLD = "lead_cold"
    NO_SHOW = "no_show"
    MANUAL = "manual"
    SCHEDULE = "schedule"


class Workflow(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    trigger_type: Mapped[WorkflowTrigger] = mapped_column(String(30), nullable=False)
    trigger_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    actions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_run_at: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    run_count: Mapped[int] = mapped_column(default=0, nullable=False)

    __table_args__ = (
        Index("ix_workflows_tenant_active", "tenant_id", "is_active"),
        Index("ix_workflows_tenant_trigger", "tenant_id", "trigger_type"),
    )


class WorkflowExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowExecution(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "workflow_executions"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[WorkflowExecutionStatus] = mapped_column(
        String(20), default=WorkflowExecutionStatus.PENDING, nullable=False, index=True
    )
    input_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    output_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("ix_workflow_executions_workflow", "workflow_id"),
        Index("ix_workflow_executions_tenant", "tenant_id"),
        Index("ix_workflow_executions_lead", "lead_id"),
    )
