"""Track AVBase release cache age and source.

Revision ID: 20260718_0004
Revises: 20260718_0003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260718_0004"
down_revision: Union[str, None] = "20260718_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INDEX_NAME = "ix_movie_data_source_last_seen"


def _existing_columns() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {
        column["name"] for column in inspector.get_columns("movie_data")
    }


def _existing_indexes() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {
        index["name"] for index in inspector.get_indexes("movie_data")
    }


def upgrade() -> None:
    columns = _existing_columns()
    if "source_type" not in columns:
        op.add_column(
            "movie_data",
            sa.Column("source_type", sa.String(), nullable=True),
        )
    if "last_seen_at" not in columns:
        op.add_column(
            "movie_data",
            sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        )

    op.get_bind().execute(
        sa.text(
            """
            UPDATE movie_data
            SET source_type = COALESCE(source_type, 'avbase_release'),
                last_seen_at = COALESCE(last_seen_at, created_at, CURRENT_TIMESTAMP)
            WHERE source_type IS NULL OR last_seen_at IS NULL
            """
        )
    )

    if INDEX_NAME not in _existing_indexes():
        op.create_index(
            INDEX_NAME,
            "movie_data",
            ["source_type", "last_seen_at"],
            unique=False,
        )


def downgrade() -> None:
    if INDEX_NAME in _existing_indexes():
        op.drop_index(INDEX_NAME, table_name="movie_data")

    columns = _existing_columns()
    if "last_seen_at" in columns:
        op.drop_column("movie_data", "last_seen_at")
    if "source_type" in columns:
        op.drop_column("movie_data", "source_type")
