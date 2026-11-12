
"""add campaign approval tracking fields

Revision ID: 3ae773511e94
Revises: 463b4663c471
Create Date: 2026-11-11 22:03:22.884309
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3ae773511e94"
down_revision: Union[str, Sequence[str], None] = "463b4663c471"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "campaigns",
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "campaigns",
        sa.Column("approved_by", sa.Integer(), nullable=True),
    )
    op.add_column(
        "campaigns",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "campaigns",
        sa.Column("rejected_by", sa.Integer(), nullable=True),
    )
    op.add_column(
        "campaigns",
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "campaigns",
        sa.Column("rejection_reason", sa.Text(), nullable=True),
    )

    op.create_foreign_key(
        "fk_campaigns_approved_by_users",
        "campaigns",
        "users",
        ["approved_by"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_campaigns_rejected_by_users",
        "campaigns",
        "users",
        ["rejected_by"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_campaigns_rejected_by_users",
        "campaigns",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_campaigns_approved_by_users",
        "campaigns",
        type_="foreignkey",
    )

    op.drop_column("campaigns", "rejection_reason")
    op.drop_column("campaigns", "rejected_at")
    op.drop_column("campaigns", "rejected_by")
    op.drop_column("campaigns", "approved_at")
    op.drop_column("campaigns", "approved_by")
    op.drop_column("campaigns", "submitted_at")
