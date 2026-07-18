"""Track complete AVBase release-date cache fetches.

Revision ID: 20260718_0006
Revises: 20260718_0005
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260718_0006"
down_revision: Union[str, None] = "20260718_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_NAME = "avbase_release_cache"
INDEX_NAME = "ix_avbase_release_cache_fetched_at"


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if TABLE_NAME not in inspector.get_table_names():
        op.create_table(
            TABLE_NAME,
            sa.Column("release_date", sa.String(), nullable=False),
            sa.Column("fetched_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("release_date"),
        )

    inspector = sa.inspect(op.get_bind())
    indexes = {
        index["name"] for index in inspector.get_indexes(TABLE_NAME)
    }
    if INDEX_NAME not in indexes:
        op.create_index(
            INDEX_NAME,
            TABLE_NAME,
            ["fetched_at"],
            unique=False,
        )

    op.get_bind().execute(
        sa.text(
            """
            INSERT OR IGNORE INTO avbase_release_cache (
                release_date,
                fetched_at
            )
            SELECT min_date, MAX(last_seen_at)
            FROM movie_data
            WHERE source_type = 'avbase_release'
              AND min_date IS NOT NULL
              AND last_seen_at IS NOT NULL
            GROUP BY min_date
            """
        )
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if TABLE_NAME in inspector.get_table_names():
        op.drop_table(TABLE_NAME)
