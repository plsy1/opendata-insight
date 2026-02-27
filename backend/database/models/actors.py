from database import Base
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class ActorData(Base):
    __tablename__ = "actor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    birthday = Column(String(20), nullable=True)
    height = Column(String(10), nullable=True)
    bust = Column(String(10), nullable=True)
    waist = Column(String(10), nullable=True)
    hip = Column(String(10), nullable=True)
    cup = Column(String(10), nullable=True)
    hobby = Column(String, nullable=True)
    prefectures = Column(String(50), nullable=True)
    blood_type = Column(String(5), nullable=True)
    aliases = Column(JSON, nullable=True)
    avatar_url = Column(String, nullable=True)
    social_media = Column(JSON, nullable=True)
    ruby = Column(String(100), nullable=True)

    subscribers = relationship(
        "ActorSubscribe",
        back_populates="actor",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ActorSubscribe(Base):
    __tablename__ = "actor_subscribe"

    actor_id = Column(Integer, ForeignKey("actor_data.id"), primary_key=True)

    is_subscribe = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    is_collect = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime, default=datetime.now)

    actor = relationship("ActorData", back_populates="subscribers")
