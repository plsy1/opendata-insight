# database.py

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Generator
from sqlalchemy.orm import relationship

DATABASE_URL = "sqlite:///./data/database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class RSSFeed(Base):
    __tablename__ = "rss_feeds"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class RSSItem(Base):
    __tablename__ = "rss_items"

    id = Column(Integer, primary_key=True, index=True)
    actors = Column(String)
    keyword = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    img = Column(String)
    link = Column(String)
    downloaded = Column(Boolean)


class ActressCollect(Base):
    __tablename__ = "actress_collect"

    id = Column(Integer, primary_key=True, index=True)
    avatar_url = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)


class EmbyMovie(Base):
    __tablename__ = "emby_movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    primary = Column(String)
    serverId = Column(String)
    indexLink = Column(String)
    ProductionYear = Column(Integer)


class FC2Metadata(Base):
    __tablename__ = "fc2_metadata"

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


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def initDatabase():
    Base.metadata.create_all(bind=engine)
