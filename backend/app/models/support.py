import enum
import uuid
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class SupportIssueType(str, enum.Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    ONBOARDING_FRICTION = "onboarding_friction"
    GENERAL_FEEDBACK = "general_feedback"
    SUPPORT_REQUEST = "support_request"

class SupportIssueStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class SupportIssuePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class SupportIssue(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Customer feedback and support issue tracking."""
    __tablename__ = "support_issues"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    issue_type: Mapped[SupportIssueType] = mapped_column(String(30), nullable=False)
    status: Mapped[SupportIssueStatus] = mapped_column(String(20), default=SupportIssueStatus.OPEN, nullable=False)
    priority: Mapped[SupportIssuePriority] = mapped_column(String(20), default=SupportIssuePriority.MEDIUM, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    category: Mapped[str | None] = mapped_column(String(50), nullable=True) # e.g. "onboarding", "billing", "chat"
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_support_issues_tenant_status", "tenant_id", "status"),
    )
