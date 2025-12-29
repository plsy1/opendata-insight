from sqlalchemy import Column, Integer, String, Boolean
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
