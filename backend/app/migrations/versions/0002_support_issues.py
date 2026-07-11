"""support issues

Revision ID: 0002_support_issues
Revises: 0001_initial_schema
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_support_issues"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "support_issues",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issue_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'open'")),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_support_issues_tenant_status", "tenant_id", "status", unique=False),
        sa.Index("ix_support_issues_tenant_id", "tenant_id", unique=False),
    )

def downgrade() -> None:
    op.drop_table("support_issues")
