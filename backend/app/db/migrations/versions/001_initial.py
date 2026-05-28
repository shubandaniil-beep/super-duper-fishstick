"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "kindergartens",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("city", sa.String(100)),
        sa.Column("address", sa.Text),
        sa.Column("phone", sa.String(30)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("kindergarten_id", UUID(as_uuid=False), sa.ForeignKey("kindergartens.id")),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30)),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("password_hash", sa.String(255)),
        sa.Column("telegram_id", sa.BigInteger, unique=True),
        sa.Column("telegram_username", sa.String(100)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "groups",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("kindergarten_id", UUID(as_uuid=False), sa.ForeignKey("kindergartens.id")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("age_from", sa.Integer),
        sa.Column("age_to", sa.Integer),
        sa.Column("teacher_id", UUID(as_uuid=False), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "children",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("kindergarten_id", UUID(as_uuid=False), sa.ForeignKey("kindergartens.id")),
        sa.Column("group_id", UUID(as_uuid=False), sa.ForeignKey("groups.id")),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("birth_date", sa.Date, nullable=False),
        sa.Column("gender", sa.String(10)),
        sa.Column("photo_url", sa.Text),
        sa.Column("allergies", sa.Text),
        sa.Column("medical_notes", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    op.create_table(
        "parent_child",
        sa.Column("parent_id", UUID(as_uuid=False), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("child_id", UUID(as_uuid=False), sa.ForeignKey("children.id"), primary_key=True),
        sa.Column("relation", sa.String(30)),
    )

    op.create_table(
        "attendance",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("child_id", UUID(as_uuid=False), sa.ForeignKey("children.id")),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("note", sa.Text),
        sa.Column("marked_by", UUID(as_uuid=False), sa.ForeignKey("users.id")),
        sa.Column("marked_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("child_id", "date", name="uq_attendance_child_date"),
    )

    op.create_table(
        "schedule",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("group_id", UUID(as_uuid=False), sa.ForeignKey("groups.id")),
        sa.Column("day_of_week", sa.Integer, nullable=False),
        sa.Column("time_start", sa.Time, nullable=False),
        sa.Column("time_end", sa.Time, nullable=False),
        sa.Column("subject", sa.String(100), nullable=False),
        sa.Column("teacher_id", UUID(as_uuid=False), sa.ForeignKey("users.id")),
        sa.Column("room", sa.String(50)),
    )

    op.create_table(
        "menu",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("kg_id", UUID(as_uuid=False), sa.ForeignKey("kindergartens.id")),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("meal_type", sa.String(20), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("calories", sa.Integer),
    )

    op.create_table(
        "posts",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("kg_id", UUID(as_uuid=False), sa.ForeignKey("kindergartens.id")),
        sa.Column("group_id", UUID(as_uuid=False), sa.ForeignKey("groups.id")),
        sa.Column("author_id", UUID(as_uuid=False), sa.ForeignKey("users.id")),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("content", sa.Text),
        sa.Column("media_urls", sa.ARRAY(sa.Text)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("is_sent", sa.Boolean, server_default="false"),
    )

    op.create_table(
        "medical_records",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("child_id", UUID(as_uuid=False), sa.ForeignKey("children.id")),
        sa.Column("record_type", sa.String(30)),
        sa.Column("title", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("date", sa.Date),
        sa.Column("next_date", sa.Date),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("child_id", UUID(as_uuid=False), sa.ForeignKey("children.id")),
        sa.Column("kg_id", UUID(as_uuid=False), sa.ForeignKey("kindergartens.id")),
        sa.Column("type", sa.String(50)),
        sa.Column("title", sa.String(255)),
        sa.Column("file_url", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "telegram_sessions",
        sa.Column("telegram_id", sa.BigInteger, primary_key=True),
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id")),
        sa.Column("state", sa.String(100)),
        sa.Column("state_data", JSONB),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "invite_codes",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("kg_id", UUID(as_uuid=False), sa.ForeignKey("kindergartens.id")),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id")),
        sa.Column("is_used", sa.Boolean, server_default="false"),
        sa.Column("expires_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    for table in [
        "invite_codes", "telegram_sessions", "documents", "medical_records",
        "posts", "menu", "schedule", "attendance", "parent_child",
        "children", "groups", "users", "kindergartens",
    ]:
        op.drop_table(table)
