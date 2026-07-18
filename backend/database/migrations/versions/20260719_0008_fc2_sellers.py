"""Add FC2 seller profiles and seller work metadata.

Revision ID: 20260719_0008
Revises: 20260718_0007
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260719_0008"
down_revision: Union[str, None] = "20260718_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PRODUCT_COLUMNS = (
    sa.Column("seller_id", sa.String(), nullable=True),
    sa.Column("description", sa.Text(), nullable=True),
    sa.Column("price", sa.String(), nullable=True),
    sa.Column("rating", sa.Integer(), nullable=True),
    sa.Column("comment_count", sa.Integer(), nullable=True),
    sa.Column("favorite_count", sa.Integer(), nullable=True),
    sa.Column("seller_page", sa.Integer(), nullable=True),
    sa.Column("seller_position", sa.Integer(), nullable=True),
)


def _column_names(table_name: str) -> set[str]:
    return {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _index_names(table_name: str) -> set[str]:
    return {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def upgrade() -> None:
    tables = set(sa.inspect(op.get_bind()).get_table_names())

    if "fc2_sellers" not in tables:
        op.create_table(
            "fc2_sellers",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("seller_id", sa.String(), nullable=False),
            sa.Column("author_id", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("profile_url", sa.String(), nullable=False),
            sa.Column("avatar_url", sa.String(), nullable=True),
            sa.Column("banner_url", sa.String(), nullable=True),
            sa.Column("short_intro", sa.Text(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("product_count", sa.Integer(), nullable=True),
            sa.Column("follower_count", sa.Integer(), nullable=True),
            sa.Column("crawled_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("seller_id"),
        )
        op.create_index(
            "ix_fc2_sellers_seller_id",
            "fc2_sellers",
            ["seller_id"],
            unique=True,
        )
        op.create_index(
            "ix_fc2_sellers_author_id",
            "fc2_sellers",
            ["author_id"],
            unique=False,
        )
        op.create_index(
            "ix_fc2_sellers_crawled_at",
            "fc2_sellers",
            ["crawled_at"],
            unique=False,
        )

    if "fc2_products" in tables:
        columns = _column_names("fc2_products")
        for column in PRODUCT_COLUMNS:
            if column.name not in columns:
                op.add_column("fc2_products", column)

        indexes = _index_names("fc2_products")
        if "ix_fc2_products_seller_id" not in indexes:
            op.create_index(
                "ix_fc2_products_seller_id",
                "fc2_products",
                ["seller_id"],
                unique=False,
            )
        if "ix_fc2_products_seller_page_position" not in indexes:
            op.create_index(
                "ix_fc2_products_seller_page_position",
                "fc2_products",
                ["seller_id", "seller_page", "seller_position"],
                unique=False,
            )

    if "fc2_ranking" in tables:
        if "seller_id" not in _column_names("fc2_ranking"):
            op.add_column(
                "fc2_ranking",
                sa.Column("seller_id", sa.String(), nullable=True),
            )
        if "ix_fc2_ranking_seller_id" not in _index_names("fc2_ranking"):
            op.create_index(
                "ix_fc2_ranking_seller_id",
                "fc2_ranking",
                ["seller_id"],
                unique=False,
            )


def downgrade() -> None:
    tables = set(sa.inspect(op.get_bind()).get_table_names())

    if "fc2_ranking" in tables and "seller_id" in _column_names("fc2_ranking"):
        if "ix_fc2_ranking_seller_id" in _index_names("fc2_ranking"):
            op.drop_index("ix_fc2_ranking_seller_id", table_name="fc2_ranking")
        op.drop_column("fc2_ranking", "seller_id")

    if "fc2_products" in tables:
        indexes = _index_names("fc2_products")
        if "ix_fc2_products_seller_page_position" in indexes:
            op.drop_index(
                "ix_fc2_products_seller_page_position",
                table_name="fc2_products",
            )
        if "ix_fc2_products_seller_id" in indexes:
            op.drop_index("ix_fc2_products_seller_id", table_name="fc2_products")
        columns = _column_names("fc2_products")
        for column in reversed(PRODUCT_COLUMNS):
            if column.name in columns:
                op.drop_column("fc2_products", column.name)

    if "fc2_sellers" in tables:
        op.drop_index("ix_fc2_sellers_crawled_at", table_name="fc2_sellers")
        op.drop_index("ix_fc2_sellers_author_id", table_name="fc2_sellers")
        op.drop_index("ix_fc2_sellers_seller_id", table_name="fc2_sellers")
        op.drop_table("fc2_sellers")
