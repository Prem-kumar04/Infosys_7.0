"""add template and message content to campaigns

Revision ID: cc3f658139a7
Revises: c959087c9421
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cc3f658139a7"
down_revision: Union[str, Sequence[str], None] = "c959087c9421"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "campaigns",
        sa.Column("template_id", sa.Integer(), nullable=True),
    )

    op.add_column(
        "campaigns",
        sa.Column("message_subject", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "campaigns",
        sa.Column("message_content", sa.Text(), nullable=True),
    )

    op.create_foreign_key(
        "fk_campaigns_template_id_campaign_templates",
        "campaigns",
        "campaign_templates",
        ["template_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_campaigns_template_id_campaign_templates",
        "campaigns",
        type_="foreignkey",
    )

    op.drop_column("campaigns", "message_content")
    op.drop_column("campaigns", "message_subject")
    op.drop_column("campaigns", "template_id")