from database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
    JSON,
)

from datetime import datetime

class FC2Product(Base):
    __tablename__ = "fc2_products"

    id = Column(Integer, primary_key=True)

    article_id = Column(String, nullable=False, index=True)

    product_id = Column(String, index=True)

    title = Column(String)
    author = Column(String)

    cover = Column(String)
    duration = Column(String)
    sale_day = Column(String)

    sample_images = Column(JSON, default=list)

    crawled_at = Column(DateTime, default=datetime.now, index=True)

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "product_id",
            name="uix_fc2_article_product",
        ),
    )

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

    rating = Column(Integer)
    comment_count = Column(Integer)
    hot_comments = Column(JSON)

    is_active = Column(Boolean, default=True, index=True)
    crawled_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("term", "article_id", "rank", name="uix_fc2_term_article"),
    )


