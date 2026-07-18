"""Track successful movie metadata refreshes.

Revision ID: 20260718_0007
Revises: 20260718_0006
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260718_0007"
down_revision: Union[str, None] = "20260718_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLUMN_NAME = "metadata_updated_at"
INDEX_NAME = "ix_movie_data_metadata_updated_at"


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {
        column["name"] for column in inspector.get_columns("movie_data")
    }
    if COLUMN_NAME not in columns:
        op.add_column(
            "movie_data",
            sa.Column(COLUMN_NAME, sa.DateTime(), nullable=True),
        )

    op.get_bind().execute(
        sa.text(
            """
            UPDATE movie_data
            SET metadata_updated_at = COALESCE(
                metadata_updated_at,
                last_seen_at,
                created_at
            )
            WHERE metadata_updated_at IS NULL
            """
        )
    )

    inspector = sa.inspect(op.get_bind())
    indexes = {
        index["name"] for index in inspector.get_indexes("movie_data")
    }
    if INDEX_NAME not in indexes:
        op.create_index(
            INDEX_NAME,
            "movie_data",
            [COLUMN_NAME],
            unique=False,
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    indexes = {
        index["name"] for index in inspector.get_indexes("movie_data")
    }
    if INDEX_NAME in indexes:
        op.drop_index(INDEX_NAME, table_name="movie_data")

    columns = {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns("movie_data")
    }
    if COLUMN_NAME in columns:
        op.drop_column("movie_data", COLUMN_NAME)
