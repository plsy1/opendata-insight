from database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime


class MovieData(Base):
    __tablename__ = "movie_data"

    id = Column(Integer, primary_key=True)
    work_id = Column(String, unique=True, index=True)
    prefix = Column(String, index=True)
    title = Column(String)
    min_date = Column(String, nullable=True)
    casts = Column(JSON, default=list)
    actors = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    genres = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.now)
    source_type = Column(String, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    metadata_updated_at = Column(DateTime, nullable=True)

    products = relationship(
        "MovieProduct", back_populates="work", cascade="all, delete-orphan"
    )

    subscribers = relationship(
        "MovieSubscribe",
        back_populates="movie",
        cascade="all, delete-orphan",
        uselist=False,
    )

    __table_args__ = (
        Index("ix_movie_data_min_date", "min_date"),
        Index(
            "ix_movie_data_source_last_seen",
            "source_type",
            "last_seen_at",
        ),
        Index("ix_movie_data_metadata_updated_at", "metadata_updated_at"),
    )


class MovieProduct(Base):
    __tablename__ = "movie_products"

    id = Column(Integer, primary_key=True)
    work_id = Column(Integer, ForeignKey("movie_data.id"), nullable=False)
    product_id = Column(String, nullable=False)

    url = Column(String)
    image_url = Column(String, nullable=True)
    title = Column(String)
    source = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    date = Column(String, nullable=True)
    maker = Column(String, nullable=True)
    label = Column(String, nullable=True)
    series = Column(String, nullable=True)
    sample_image_urls = Column(JSON, default=list)
    director = Column(String, nullable=True)
    price = Column(String, nullable=True)
    volume = Column(String, nullable=True)

    work = relationship("MovieData", back_populates="products")

    __table_args__ = (
        UniqueConstraint("work_id", "product_id", name="uix_work_product"),
    )


class MovieSubscribe(Base):
    __tablename__ = "movie_subscribe"

    movie_id = Column(Integer, ForeignKey("movie_data.id"), primary_key=True)

    is_downloaded = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime, default=datetime.now)

    # NULL means this movie follows the global subscription filters. A JSON
    # object, including an empty one, is an explicit per-movie override.
    rule_config = Column(JSON, nullable=True)

    movie = relationship("MovieData", back_populates="subscribers")

    __table_args__ = (
        Index(
            "ix_movie_subscribe_downloaded_created_at",
            "is_downloaded",
            "created_at",
        ),
    )
