"""Add indexes used by the application's common queries.

Revision ID: 20260718_0002
Revises: 20260718_0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260718_0002"
down_revision: Union[str, None] = "20260718_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INDEXES = (
    ("ix_actor_data_name", "actor_data", ["name"]),
    ("ix_movie_data_min_date", "movie_data", ["min_date"]),
    (
        "ix_fc2_ranking_term_page_rank",
        "fc2_ranking",
        ["term", "page", "rank"],
    ),
    (
        "ix_movie_subscribe_downloaded_created_at",
        "movie_subscribe",
        ["is_downloaded", "created_at"],
    ),
    (
        "ix_actor_subscribe_subscribed_order",
        "actor_subscribe",
        ["is_subscribe", "subscribe_order", "created_at"],
    ),
    (
        "ix_actor_subscribe_collected_order",
        "actor_subscribe",
        ["is_collect", "collect_order", "created_at"],
    ),
    ("ix_image_sources_updated_at", "image_sources", ["updated_at"]),
)


def _existing_indexes(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    for index_name, table_name, columns in INDEXES:
        if index_name not in _existing_indexes(table_name):
            op.create_index(index_name, table_name, columns, unique=False)


def downgrade() -> None:
    for index_name, table_name, _columns in reversed(INDEXES):
        if index_name in _existing_indexes(table_name):
            op.drop_index(index_name, table_name=table_name)
