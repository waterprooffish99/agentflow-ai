import uuid
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class FAQEntry(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Knowledge base entries for AI context."""
    __tablename__ = "faq_entries"

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
