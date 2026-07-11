"""experiments

Revision ID: 0005_experiments
Revises: 0004_incidents
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_experiments"
down_revision = "0004_incidents"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("target_percentage", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("target_tiers", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("variants", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "tenant_experiment_assignments",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("experiment_name", sa.String(length=100), nullable=False),
        sa.Column("variant_name", sa.String(length=50), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_tenant_experiment_assignment", "tenant_id", "experiment_name", unique=True),
    )

def downgrade() -> None:
    op.drop_table("tenant_experiment_assignments")
    op.drop_table("experiments")
