from database import Base
from sqlalchemy import Column, Integer, String


class EmbyMovie(Base):
    __tablename__ = "emby_movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    primary = Column(String)
    serverId = Column(String)
    indexLink = Column(String)
    ProductionYear = Column(Integer)
