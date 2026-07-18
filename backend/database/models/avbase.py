from sqlalchemy import Column, DateTime, Index, Integer, String
from database import Base


class avbaseNewbie(Base):
    __tablename__ = "avbase_newbie"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    avatar_url = Column(String, nullable=True)


class avbasePopular(Base):
    __tablename__ = "avbase_popular"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    avatar_url = Column(String, nullable=True)


class AvbaseReleaseCache(Base):
    __tablename__ = "avbase_release_cache"

    release_date = Column(String, primary_key=True)
    fetched_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_avbase_release_cache_fetched_at", "fetched_at"),
    )
