import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

class BusinessProfile(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """Detailed business profile for a tenant."""
    __tablename__ = "business_profiles"

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Optional: Link to tenant explicitly if needed, though TenantMixin covers isolation
    # tenant = relationship("Tenant", backref="profile")
