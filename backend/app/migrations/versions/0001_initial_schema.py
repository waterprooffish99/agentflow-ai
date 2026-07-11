"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("business_name", sa.String(length=100), nullable=False),
        sa.Column("domain", sa.String(length=255)),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default=sa.text("'UTC'")),
        sa.Column("subscription_tier", sa.String(length=20), nullable=False, server_default=sa.text("'SubscriptionTier.FREE'")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'TenantStatus.TRIAL'")),
        sa.Column("lead_source", sa.String(length=50), nullable=True),
        sa.Column("campaign_source", sa.String(length=50), nullable=True),
        sa.Column("referral_source", sa.String(length=255), nullable=True),
        sa.Column("acquisition_channel", sa.String(length=50), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("settings", postgresql.JSONB(), nullable=False),
        sa.Column("ai_config", postgresql.JSONB(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_tenants_status", "status", unique=False),
        sa.Index("ix_tenants_business_name", "business_name", unique=True),
        sa.Index("ix_tenants_lead_source", "lead_source", unique=False),
        sa.Index("ix_tenants_acquisition_channel", "acquisition_channel", unique=False),
    )

    op.create_table(
        "users",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'UserStatus.ACTIVE'")),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_login", sa.DateTime(timezone=True)),
        sa.Column("email_verify_token", sa.String(length=255)),
        sa.Column("password_reset_token", sa.String(length=255)),
        sa.Column("password_reset_expires", sa.DateTime(timezone=True)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_users_email", "email", unique=True),
        sa.Index("ix_users_tenant_role", "tenant_id", "role", unique=False),
    )

    op.create_table(
        "customers",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255)),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("location", sa.String(length=100)),
        sa.Column("preferences", postgresql.JSONB(), nullable=False),
        sa.Column("total_bookings", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_customers_tenant_email", "tenant_id", "email", unique=True),
        sa.Index("ix_customers_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_customers_tenant_phone", "tenant_id", "phone", unique=True),
        sa.Index("ix_customers_phone", "phone", unique=False),
        sa.Index("ix_customers_email", "email", unique=False),
    )

    op.create_table(
        "customer_tags",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("color", sa.String(length=7)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_customer_tags_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_customer_tags_tenant_name", "tenant_id", "name", unique=True),
    )

    op.create_table(
        "lead_pipeline_stages",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_winning_stage", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_losing_stage", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_lead_pipeline_stages_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_lead_pipeline_stages_tenant_order", "tenant_id", "order", unique=False),
    )

    op.create_table(
        "services",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("price", sa.Numeric(precision=10, scale=2)),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default=sa.text("30")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_services_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "staff_members",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255)),
        sa.Column("role", sa.String(length=50)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_staff_members_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "leads",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True)),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), ),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'LeadStatus.UNQUALIFIED'")),
        sa.Column("source", sa.String(length=50)),
        sa.Column("urgency", sa.String(length=20), nullable=False, server_default=sa.text("'LeadUrgency.MEDIUM'")),
        sa.Column("budget_range", sa.String(length=50)),
        sa.Column("preferred_service", sa.String(length=100)),
        sa.Column("preferred_times", postgresql.JSONB(), nullable=False),
        sa.Column("conversation_summary", sa.Text()),
        sa.Column("qualifies_reason", sa.Text()),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_leads_status", "status", unique=False),
        sa.Index("ix_leads_tenant_status", "tenant_id", "status", unique=False),
        sa.Index("ix_leads_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_leads_assigned_to", "assigned_to", unique=False),
        sa.Index("ix_leads_tenant_created", "tenant_id", "created_at", unique=False),
    )

    op.create_table(
        "conversations",
        sa.Column("lead_id", postgresql.UUID(as_uuid=True)),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), ),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'ConversationStatus.ACTIVE'")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("escalated_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), ),
        sa.Column("escalated_reason", sa.String(length=255)),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), ),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_conversations_status", "status", unique=False),
        sa.Index("ix_conversations_lead", "lead_id", unique=False),
        sa.Index("ix_conversations_tenant_status", "tenant_id", "status", unique=False),
        sa.Index("ix_conversations_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "ai_configurations",
        sa.Column("name", sa.String(length=100), nullable=False, server_default=sa.text("'default'")),
        sa.Column("system_prompt", sa.Text()),
        sa.Column("personality_traits", postgresql.JSONB(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False, server_default=sa.text("0.7")),
        sa.Column("model_name", sa.String(length=100), nullable=False, server_default=sa.text("'gpt-4'")),
        sa.Column("tools_enabled", postgresql.JSONB(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_ai_configurations_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("details", postgresql.JSONB()),
        sa.Column("ip_address", sa.String(length=45)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Index("ix_audit_logs_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_audit_logs_timestamp", "timestamp", unique=False),
        sa.Index("ix_audit_tenant_timestamp", "tenant_id", "timestamp", unique=False),
    )

    op.create_table(
        "business_profiles",
        sa.Column("description", sa.Text()),
        sa.Column("address", sa.String(length=255)),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("website", sa.String(length=255)),
        sa.Column("industry", sa.String(length=100)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_business_profiles_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "faq_entries",
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_faq_entries_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "notifications",
        sa.Column("recipient_type", sa.String(length=20), nullable=False),
        sa.Column("recipient_address", sa.String(length=255), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("template", sa.String(length=100), nullable=False),
        sa.Column("context", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'NotificationStatus.PENDING'")),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text()),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_notifications_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_notifications_tenant_channel", "tenant_id", "channel", unique=False),
        sa.Index("ix_notifications_tenant_status", "tenant_id", "status", unique=False),
        sa.Index("ix_notifications_status", "status", unique=False),
    )

    op.create_table(
        "workflows",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500)),
        sa.Column("trigger_type", sa.String(length=30), nullable=False),
        sa.Column("trigger_config", postgresql.JSONB(), nullable=False),
        sa.Column("actions", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_run_at", postgresql.UUID(as_uuid=True)),
        sa.Column("run_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_workflows_tenant_trigger", "tenant_id", "trigger_type", unique=False),
        sa.Index("ix_workflows_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_workflows_tenant_active", "tenant_id", "is_active", unique=False),
    )

    op.create_table(
        "conversation_memory",
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary", sa.String(length=None)),
        sa.Column("facts", postgresql.JSONB(), nullable=False),
        sa.Column("ai_state", postgresql.JSONB(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_conversation_memory_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_conversation_memory_conversation", "conversation_id", unique=False),
        sa.Index("ix_conversation_memory_tenant", "tenant_id", unique=False),
    )

    op.create_table(
        "customer_activities",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True)),
        sa.Column("reference_type", sa.String(length=50)),
        sa.Column("metadata", postgresql.JSONB(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_customer_activities_customer", "customer_id", unique=False),
        sa.Index("ix_customer_activities_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_customer_activities_tenant", "tenant_id", unique=False),
    )

    op.create_table(
        "customer_tag_links",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customer_tags.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Index("ix_customer_tag_links_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "lead_captures",
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_name", sa.String(length=50), nullable=False),
        sa.Column("field_value", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("capture_metadata", postgresql.JSONB()),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_lead_captures_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_lead_captures_lead", "lead_id", unique=False),
        sa.Index("ix_lead_captures_conversation", "conversation_id", unique=False),
        sa.Index("ix_lead_captures_tenant", "tenant_id", unique=False),
    )

    op.create_table(
        "lead_stage_history",
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lead_pipeline_stages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True)),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_lead_stage_history_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_lead_stage_history_lead", "lead_id", unique=False),
        sa.Index("ix_lead_stage_history_tenant", "tenant_id", unique=False),
    )

    op.create_table(
        "messages",
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.String(length=None), nullable=False),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_messages_tenant", "tenant_id", unique=False),
        sa.Index("ix_messages_conversation", "conversation_id", unique=False),
        sa.Index("ix_messages_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "customer_notes",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), ),
        sa.Column("is_ai_generated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_customer_notes_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_customer_notes_tenant", "tenant_id", unique=False),
        sa.Index("ix_customer_notes_customer", "customer_id", unique=False),
    )

    op.create_table(
        "follow_up_tasks",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), ),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'FollowUpStatus.PENDING'")),
        sa.Column("is_automated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("completion_notes", sa.Text()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_follow_up_tasks_customer", "customer_id", unique=False),
        sa.Index("ix_follow_up_tasks_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_follow_up_tasks_status", "status", unique=False),
        sa.Index("ix_follow_up_tasks_tenant_due", "tenant_id", "due_at", unique=False),
    )

    op.create_table(
        "appointments",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), ),
        sa.Column("staff_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("staff_members.id", ondelete="SET NULL"), ),
        sa.Column("service_type", sa.String(length=100), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'AppointmentStatus.CONFIRMED'")),
        sa.Column("notes", sa.Text()),
        sa.Column("cancelled_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), ),
        sa.Column("cancelled_reason", sa.String(length=255)),
        sa.Column("rescheduled_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("appointments.id", ondelete="SET NULL"), ),
        sa.Column("rescheduled_from_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("appointments.id", ondelete="SET NULL"), ),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_appointments_tenant_id", "tenant_id", unique=False),
        sa.Index("ix_appointments_customer", "customer_id", unique=False),
        sa.Index("ix_appointments_tenant_start", "tenant_id", "start_time", unique=False),
        sa.Index("ix_appointments_status", "status", unique=False),
        sa.Index("ix_appointments_lead", "lead_id", unique=False),
    )

    op.create_table(
        "availability_exceptions",
        sa.Column("staff_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("staff_members.id", ondelete="CASCADE"), ),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reason", sa.String(length=255)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_availability_exceptions_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "availability_rules",
        sa.Column("staff_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("staff_members.id", ondelete="CASCADE"), ),
        sa.Column("day_of_week", sa.String(length=20), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_availability_rules_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "calendar_connections",
        sa.Column("staff_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("staff_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("external_calendar_id", sa.String(length=255), nullable=False),
        sa.Column("credentials", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sync_token", sa.String(length=255)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_calendar_connections_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "booking_events",
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("actor_type", sa.String(length=20), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column("description", sa.Text()),
        sa.Column("metadata", postgresql.JSONB(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_booking_events_tenant_id", "tenant_id", unique=False),
    )

    op.create_table(
        "workflow_executions",
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), ),
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("appointments.id", ondelete="SET NULL"), ),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'WorkflowExecutionStatus.PENDING'")),
        sa.Column("input_data", postgresql.JSONB(), nullable=False),
        sa.Column("output_data", postgresql.JSONB(), nullable=False),
        sa.Column("error", sa.String(length=None)),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Index("ix_workflow_executions_status", "status", unique=False),
        sa.Index("ix_workflow_executions_lead", "lead_id", unique=False),
        sa.Index("ix_workflow_executions_workflow", "workflow_id", unique=False),
        sa.Index("ix_workflow_executions_tenant", "tenant_id", unique=False),
        sa.Index("ix_workflow_executions_tenant_id", "tenant_id", unique=False),
    )

    op.create_foreign_key("fk_leads_conversation", "leads", "conversations", ["conversation_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_conversations_lead", "conversations", "leads", ["lead_id"], ["id"], ondelete="CASCADE")

def downgrade() -> None:
    op.drop_table("workflow_executions")
    op.drop_table("booking_events")
    op.drop_table("calendar_connections")
    op.drop_table("availability_rules")
    op.drop_table("availability_exceptions")
    op.drop_table("appointments")
    op.drop_table("staff_members")
    op.drop_table("follow_up_tasks")
    op.drop_table("customer_notes")
    op.drop_table("users")
    op.drop_table("messages")
    op.drop_table("lead_stage_history")
    op.drop_table("lead_captures")
    op.drop_table("customer_tag_links")
    op.drop_table("customer_activities")
    op.drop_table("conversation_memory")
    op.drop_table("workflows")
    op.drop_table("tenants")
    op.drop_table("services")
    op.drop_table("notifications")
    op.drop_table("leads")
    op.drop_table("lead_pipeline_stages")
    op.drop_table("faq_entries")
    op.drop_table("customers")
    op.drop_table("customer_tags")
    op.drop_table("conversations")
    op.drop_table("business_profiles")
    op.drop_table("audit_logs")
    op.drop_table("ai_configurations")
