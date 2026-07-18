"""Add per-movie subscription matching rules.

Revision ID: 20260718_0003
Revises: 20260718_0002
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260718_0003"
down_revision: Union[str, None] = "20260718_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _existing_columns() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {
        column["name"]
        for column in inspector.get_columns("movie_subscribe")
    }


def upgrade() -> None:
    if "rule_config" not in _existing_columns():
        op.add_column(
            "movie_subscribe",
            sa.Column("rule_config", sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    if "rule_config" in _existing_columns():
        op.drop_column("movie_subscribe", "rule_config")
