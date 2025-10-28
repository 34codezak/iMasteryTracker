"""create initial mastery tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_create_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learningstream",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("focus", sa.String(), nullable=False, server_default=""),
        sa.Column("milestones_total", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("milestones_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("color", sa.String(), nullable=False, server_default="#6366F1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "habit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("cadence", sa.String(), nullable=False, server_default="Daily"),
        sa.Column("context", sa.String(), nullable=False, server_default=""),
        sa.Column("last_completed_on", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "journalentry",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("reflection", sa.String(), nullable=False),
        sa.Column("mood", sa.String(), nullable=False, server_default="Curious"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("journalentry")
    op.drop_table("habit")
    op.drop_table("learningstream")
