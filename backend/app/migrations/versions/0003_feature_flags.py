"""feature flags

Revision ID: 0003_feature_flags
Revises: 0002_support_issues
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_feature_flags"
down_revision = "0002_support_issues"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "feature_flags",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'disabled'")),
        sa.Column("rollout_percentage", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("allowed_tiers", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "tenant_feature_overrides",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_name", sa.String(length=100), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_tenant_feature_override", "tenant_id", "feature_name", unique=True),
    )

def downgrade() -> None:
    op.drop_table("tenant_feature_overrides")
    op.drop_table("feature_flags")
