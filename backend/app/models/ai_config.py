import uuid
from sqlalchemy import String, Text, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class AIConfiguration(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """AI agent behavioral settings per tenant."""
    __tablename__ = "ai_configurations"

    name: Mapped[str] = mapped_column(String(100), default="default", nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality_traits: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="gpt-4", nullable=False)
    tools_enabled: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)
