"""incidents

Revision ID: 0004_incidents
Revises: 0003_feature_flags
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_incidents"
down_revision = "0003_feature_flags"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'open'")),
        sa.Column("component", sa.String(length=100), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_incidents_status_severity", "status", "severity", unique=False),
    )

def downgrade() -> None:
    op.drop_table("incidents")
