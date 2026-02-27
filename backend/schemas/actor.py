from pydantic import BaseModel, Field
from typing import List, Optional


class SocialMedia(BaseModel):
    platform: str = ""
    username: str = ""
    link: str = ""


class ActorDataOut(BaseModel):
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
    aliases: Optional[List[str]] = Field(default_factory=list)
    avatar_url: Optional[str] = None
    social_media: Optional[List[SocialMedia]] = Field(default_factory=list)
    ruby: Optional[str] = None

    model_config = {"from_attributes": True}


class AvbaseIndexActorOut(BaseModel):
    name: str
    avatar_url: Optional[str] = None
    model_config = {"from_attributes": True}
