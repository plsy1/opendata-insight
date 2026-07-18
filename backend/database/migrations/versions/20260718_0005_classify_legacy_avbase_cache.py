"""Classify legacy AVBase cache records conservatively.

Revision ID: 20260718_0005
Revises: 20260718_0004
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260718_0005"
down_revision: Union[str, None] = "20260718_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(
        sa.text(
            """
            UPDATE movie_data
            SET source_type = 'avbase_detail'
            WHERE source_type = 'avbase_release'
              AND (
                  created_at IS NULL
                  OR min_date IS NULL
                  OR ABS(julianday(created_at) - julianday(min_date)) > 2
              )
            """
        )
    )


def downgrade() -> None:
    pass
