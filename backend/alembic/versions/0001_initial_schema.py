"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("admin", "coach", "support", "affiliate", "user", name="userrole"), nullable=False, server_default="user"),
        sa.Column("status", sa.Enum("active", "inactive", "banned", name="userstatus"), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("position", sa.String(100), nullable=True),
        sa.Column("team", sa.String(255), nullable=True),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("weight", sa.Float, nullable=True),
        sa.Column("height", sa.Float, nullable=True),
        sa.Column("training_frequency", sa.Integer, nullable=True),
        sa.Column("goals", postgresql.JSONB, nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("next_game_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("plan", sa.Enum("trial", "monthly", "yearly", name="subscriptionplan"), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("status", sa.Enum("active", "cancelled", "expired", "past_due", "trialing", name="subscriptionstatus"), nullable=False, server_default="trialing"),
        sa.Column("trial_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_billing", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_provider", sa.Enum("stripe", "tranzila", "payme", name="paymentprovider"), nullable=True),
        sa.Column("provider_subscription_id", sa.String(255), nullable=True),
        sa.Column("provider_customer_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])

    op.create_table(
        "content",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.Enum("video", "zoom", "podcast", "challenge", "article", name="contenttype"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("vimeo_id", sa.String(100), nullable=True),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column("duration_sec", sa.Integer, nullable=True),
        sa.Column("topic_category", sa.String(100), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_free", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_content_type", "content", ["type"])
    op.create_index("ix_content_published_at", "content", ["published_at"])

    op.create_table(
        "content_views",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content.id", ondelete="CASCADE"), nullable=False),
        sa.Column("watched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completion_pct", sa.Float, nullable=False, server_default="0"),
    )
    op.create_index("ix_content_views_user_id", "content_views", ["user_id"])

    op.create_table(
        "challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("points", sa.Integer, nullable=False, server_default="10"),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("type", sa.Enum("daily", "weekly", "seasonal", name="challengetype"), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "challenge_completions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("evidence_url", sa.String(500), nullable=True),
    )
    op.create_index("ix_challenge_completions_user_id", "challenge_completions", ["user_id"])

    op.create_table(
        "user_points",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("total_points", sa.Integer, nullable=False, server_default="0"),
        sa.Column("rank", sa.Enum("bronze", "silver", "gold", "champion", name="userrank"), nullable=False, server_default="bronze"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "ai_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("messages", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ai_sessions_user_id", "ai_sessions", ["user_id"])

    op.create_table(
        "affiliates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("commission_pct", sa.Float, nullable=False, server_default="15.0"),
        sa.Column("total_earned", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_affiliates_code", "affiliates", ["code"])

    op.create_table(
        "referrals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("referred_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("commission_amount", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "notifications_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.Enum("push", "email", "whatsapp", name="notificationchannel"), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_notifications_log_user_id", "notifications_log", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications_log")
    op.drop_table("referrals")
    op.drop_table("affiliates")
    op.drop_table("ai_sessions")
    op.drop_table("user_points")
    op.drop_table("challenge_completions")
    op.drop_table("challenges")
    op.drop_table("content_views")
    op.drop_table("content")
    op.drop_table("subscriptions")
    op.drop_table("profiles")
    op.drop_table("users")
    # Drop enums
    for enum in ["userrole", "userstatus", "subscriptionplan", "subscriptionstatus",
                 "paymentprovider", "contenttype", "challengetype", "userrank", "notificationchannel"]:
        op.execute(f"DROP TYPE IF EXISTS {enum}")
