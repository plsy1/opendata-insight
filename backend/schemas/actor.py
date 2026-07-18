from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional


class SocialMedia(BaseModel):
    platform: str = ""
    username: str = ""
    link: str = ""


class ActorSubscriptionOut(BaseModel):
    actor_id: int
    is_subscribe: bool
    is_collect: bool
    subscribe_order: int
    collect_order: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "allow"}


class ActorDataOut(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    birthday: Optional[str] = None
    height: Optional[str] = None
    bust: Optional[str] = None
    waist: Optional[str] = None
    hip: Optional[str] = None
    cup: Optional[str] = None
    hobby: Optional[str] = None
    prefectures: Optional[str] = None
    blood_type: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    avatar_url: Optional[str] = None
    social_media: List[SocialMedia] = Field(default_factory=list)
    ruby: Optional[str] = None
    updated_at: Optional[datetime] = None
    subscribers: Optional[ActorSubscriptionOut] = None

    model_config = {"from_attributes": True, "extra": "allow"}

    @field_validator("aliases", "social_media", mode="before")
    @classmethod
    def _normalize_lists(cls, value):
        return value or []


class AvbaseIndexActorOut(BaseModel):
    id: Optional[int] = None
    name: str
    avatar_url: Optional[str] = None
    model_config = {"from_attributes": True, "extra": "allow"}


class AvbaseIndexOut(BaseModel):
    newbie_talents: List[AvbaseIndexActorOut] = Field(default_factory=list)
    popular_talents: List[AvbaseIndexActorOut] = Field(default_factory=list)


class ActorListOut(ActorDataOut):
    id: int


class ActorOrderUpdate(BaseModel):
    type: str
    names: List[str]
