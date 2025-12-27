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
    casts = Column(JSON, default=[])
    actors = Column(JSON, default=[])
    tags = Column(JSON, default=[])
    genres = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.now)

    products = relationship(
        "MovieProduct", back_populates="work", cascade="all, delete-orphan"
    )

    subscribers = relationship(
        "MovieSubscribe",
        back_populates="movie",
        cascade="all, delete-orphan",
        uselist=False,
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
    sample_image_urls = Column(JSON, default=[])
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

    movie = relationship("MovieData", back_populates="subscribers")
