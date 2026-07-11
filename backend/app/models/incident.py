import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, String, Text, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin

class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Incident(Base, UUIDMixin, TimestampMixin):
    """Platform-level incident tracking for production stabilization."""
    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(String(20), default=IncidentSeverity.MEDIUM, nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(String(20), default=IncidentStatus.OPEN, nullable=False)
    
    component: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "redis", "openai", "db"
    
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_incidents_status_severity", "status", "severity"),
    )
