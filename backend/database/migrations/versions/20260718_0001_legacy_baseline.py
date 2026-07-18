"""Create the legacy application schema for new installations.

Revision ID: 20260718_0001
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260718_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "actor_data",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("birthday", sa.String(length=20), nullable=True),
        sa.Column("height", sa.String(length=10), nullable=True),
        sa.Column("bust", sa.String(length=10), nullable=True),
        sa.Column("waist", sa.String(length=10), nullable=True),
        sa.Column("hip", sa.String(length=10), nullable=True),
        sa.Column("cup", sa.String(length=10), nullable=True),
        sa.Column("hobby", sa.String(), nullable=True),
        sa.Column("prefectures", sa.String(length=50), nullable=True),
        sa.Column("blood_type", sa.String(length=5), nullable=True),
        sa.Column("aliases", sa.JSON(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("social_media", sa.JSON(), nullable=True),
        sa.Column("ruby", sa.String(length=100), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "avbase_newbie",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "avbase_popular",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "emby_movies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("primary", sa.String(), nullable=True),
        sa.Column("serverId", sa.String(), nullable=True),
        sa.Column("indexLink", sa.String(), nullable=True),
        sa.Column("ProductionYear", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_emby_movies_id", "emby_movies", ["id"], unique=False)
    op.create_index("ix_emby_movies_name", "emby_movies", ["name"], unique=False)

    op.create_table(
        "fc2_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("cover", sa.String(), nullable=True),
        sa.Column("duration", sa.String(), nullable=True),
        sa.Column("sale_day", sa.String(), nullable=True),
        sa.Column("sample_images", sa.JSON(), nullable=True),
        sa.Column("crawled_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "article_id", "product_id", name="uix_fc2_article_product"
        ),
    )
    op.create_index(
        "ix_fc2_products_article_id", "fc2_products", ["article_id"], unique=False
    )
    op.create_index(
        "ix_fc2_products_crawled_at", "fc2_products", ["crawled_at"], unique=False
    )
    op.create_index(
        "ix_fc2_products_product_id", "fc2_products", ["product_id"], unique=False
    )

    op.create_table(
        "fc2_ranking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(), nullable=False),
        sa.Column("article_id", sa.String(), nullable=False),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("cover", sa.String(), nullable=True),
        sa.Column("owner", sa.String(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("comment_count", sa.Integer(), nullable=True),
        sa.Column("hot_comments", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("crawled_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "term", "article_id", "rank", name="uix_fc2_term_article"
        ),
    )
    op.create_index(
        "ix_fc2_ranking_article_id", "fc2_ranking", ["article_id"], unique=False
    )
    op.create_index(
        "ix_fc2_ranking_is_active", "fc2_ranking", ["is_active"], unique=False
    )
    op.create_index("ix_fc2_ranking_term", "fc2_ranking", ["term"], unique=False)

    op.create_table(
        "movie_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("work_id", sa.String(), nullable=True),
        sa.Column("prefix", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("min_date", sa.String(), nullable=True),
        sa.Column("casts", sa.JSON(), nullable=True),
        sa.Column("actors", sa.JSON(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("genres", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_movie_data_prefix", "movie_data", ["prefix"], unique=False)
    op.create_index("ix_movie_data_work_id", "movie_data", ["work_id"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "actor_subscribe",
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("is_subscribe", sa.Boolean(), nullable=False),
        sa.Column("is_collect", sa.Boolean(), nullable=False),
        sa.Column("subscribe_order", sa.Integer(), nullable=False),
        sa.Column("collect_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["actor_id"], ["actor_data.id"]),
        sa.PrimaryKeyConstraint("actor_id"),
    )
    op.create_index(
        "ix_actor_subscribe_is_collect",
        "actor_subscribe",
        ["is_collect"],
        unique=False,
    )
    op.create_index(
        "ix_actor_subscribe_is_subscribe",
        "actor_subscribe",
        ["is_subscribe"],
        unique=False,
    )

    op.create_table(
        "movie_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("work_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("thumbnail_url", sa.String(), nullable=True),
        sa.Column("date", sa.String(), nullable=True),
        sa.Column("maker", sa.String(), nullable=True),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("series", sa.String(), nullable=True),
        sa.Column("sample_image_urls", sa.JSON(), nullable=True),
        sa.Column("director", sa.String(), nullable=True),
        sa.Column("price", sa.String(), nullable=True),
        sa.Column("volume", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["work_id"], ["movie_data.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("work_id", "product_id", name="uix_work_product"),
    )

    op.create_table(
        "movie_subscribe",
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("is_downloaded", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["movie_id"], ["movie_data.id"]),
        sa.PrimaryKeyConstraint("movie_id"),
    )
    op.create_index(
        "ix_movie_subscribe_is_downloaded",
        "movie_subscribe",
        ["is_downloaded"],
        unique=False,
    )

    op.create_table(
        "image_sources",
        sa.Column("image_id", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("content_etag", sa.String(), nullable=True),
        sa.Column("upstream_etag", sa.String(), nullable=True),
        sa.Column("upstream_last_modified", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("image_id"),
    )


def downgrade() -> None:
    op.drop_table("image_sources")
    op.drop_index("ix_movie_subscribe_is_downloaded", table_name="movie_subscribe")
    op.drop_table("movie_subscribe")
    op.drop_table("movie_products")
    op.drop_index("ix_actor_subscribe_is_subscribe", table_name="actor_subscribe")
    op.drop_index("ix_actor_subscribe_is_collect", table_name="actor_subscribe")
    op.drop_table("actor_subscribe")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_movie_data_work_id", table_name="movie_data")
    op.drop_index("ix_movie_data_prefix", table_name="movie_data")
    op.drop_table("movie_data")
    op.drop_index("ix_fc2_ranking_term", table_name="fc2_ranking")
    op.drop_index("ix_fc2_ranking_is_active", table_name="fc2_ranking")
    op.drop_index("ix_fc2_ranking_article_id", table_name="fc2_ranking")
    op.drop_table("fc2_ranking")
    op.drop_index("ix_fc2_products_product_id", table_name="fc2_products")
    op.drop_index("ix_fc2_products_crawled_at", table_name="fc2_products")
    op.drop_index("ix_fc2_products_article_id", table_name="fc2_products")
    op.drop_table("fc2_products")
    op.drop_index("ix_emby_movies_name", table_name="emby_movies")
    op.drop_index("ix_emby_movies_id", table_name="emby_movies")
    op.drop_table("emby_movies")
    op.drop_table("avbase_popular")
    op.drop_table("avbase_newbie")
    op.drop_table("actor_data")
