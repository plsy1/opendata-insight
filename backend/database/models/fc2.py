from database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
    JSON,
    Index,
    Text,
)

from datetime import datetime

class FC2Product(Base):
    __tablename__ = "fc2_products"

    id = Column(Integer, primary_key=True)

    article_id = Column(String, nullable=False, index=True)

    product_id = Column(String, index=True)

    title = Column(String)
    author = Column(String)
    seller_id = Column(String, index=True)

    cover = Column(String)
    duration = Column(String)
    sale_day = Column(String)
    description = Column(Text)
    price = Column(String)
    rating = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    seller_page = Column(Integer)
    seller_position = Column(Integer)

    sample_images = Column(JSON, default=list)

    crawled_at = Column(DateTime, default=datetime.now, index=True)

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "product_id",
            name="uix_fc2_article_product",
        ),
        Index(
            "ix_fc2_products_seller_page_position",
            "seller_id",
            "seller_page",
            "seller_position",
        ),
    )

    @property
    def seller_url(self):
        if not self.seller_id:
            return None
        return f"https://adult.contents.fc2.com/users/{self.seller_id}/"


class FC2Seller(Base):
    __tablename__ = "fc2_sellers"

    id = Column(Integer, primary_key=True)
    seller_id = Column(String, nullable=False, unique=True, index=True)
    author_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    profile_url = Column(String, nullable=False)
    avatar_url = Column(String)
    banner_url = Column(String)
    short_intro = Column(Text)
    description = Column(Text)
    product_count = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    crawled_at = Column(DateTime, default=datetime.now, index=True)

class FC2Ranking(Base):
    __tablename__ = "fc2_ranking"

    id = Column(Integer, primary_key=True)

    term = Column(String, nullable=False, index=True)
    article_id = Column(String, nullable=False, index=True)

    page = Column(Integer)
    rank = Column(Integer)

    title = Column(String)
    url = Column(String)
    cover = Column(String)
    owner = Column(String)
    seller_id = Column(String, index=True)

    rating = Column(Integer)
    comment_count = Column(Integer)
    hot_comments = Column(JSON)

    is_active = Column(Boolean, default=True, index=True)
    crawled_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("term", "article_id", "rank", name="uix_fc2_term_article"),
        Index("ix_fc2_ranking_term_page_rank", "term", "page", "rank"),
    )

    @property
    def seller_url(self):
        if not self.seller_id:
            return None
        return f"https://adult.contents.fc2.com/users/{self.seller_id}/"
