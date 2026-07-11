import uuid
from sqlalchemy import String, Text, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class Service(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Services offered by a business."""
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
