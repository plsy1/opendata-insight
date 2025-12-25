
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from datetime import datetime

class Talent(BaseModel):
    id: int = 0
    deleted_at: Optional[str] = None


class Actor(BaseModel):
    id: int = 0
    name: str = ""
    order: Optional[int] = None
    image_url: Optional[str] = None
    talent: Optional[Talent] = None
    ruby: Optional[str] = None
    note: Optional[str] = None
    

    @field_validator('image_url', mode='before')
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class Cast(BaseModel):
    actor: Actor = Actor()
    note: Optional[str] = None


class MakerLabelSeries(BaseModel):
    name: str = ""


class ProductItemInfo(BaseModel):
    director: Optional[str] = None
    price: Optional[str] = None
    volume: Optional[str] = None


class Product(BaseModel):
    id: int = 0
    product_id: str = ""
    url: str = ""
    image_url: Optional[str] = None
    title: str = ""
    source: Optional[str] = None
    thumbnail_url: str = ""
    date: Optional[str] = None
    maker: Optional[MakerLabelSeries] = MakerLabelSeries()
    label: Optional[MakerLabelSeries] = MakerLabelSeries()
    series: Optional[MakerLabelSeries] = MakerLabelSeries()
    sample_image_urls: List[dict] = []
    iteminfo: Optional[ProductItemInfo] = ProductItemInfo()
    

    @field_validator('image_url', mode='before')
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class Genre(BaseModel):
    id: int = 0
    name: str = ""
    canonical_id: Optional[Union[str, int]] = None


class Work(BaseModel):
    id: int = 0
    prefix: str = ""
    work_id: str = ""
    title: str = ""
    min_date: Optional[str] = None
    note: Optional[str] = None
    casts: List[Cast] = []
    actors: List[Actor] = []
    tags: List = []
    genres: List[Genre] = []
    products: List[Product] = []
    
    
class AvbaseEverydayReleaseByPrefix(BaseModel):
    prefixName: str
    works:List[Work] = []

class SocialMedia(BaseModel):
    platform: str = ""
    username: str = ""
    link: str = ""


class Actress(BaseModel):
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
    raw_avatar_url: Optional[str] = None
    social_media: Optional[List[SocialMedia]] = Field(default_factory=list)

    model_config = {
        "from_attributes": True
    }
    

class Movie(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: List[str]










class MovieProductOut(BaseModel):
    product_id: str
    url: str
    image_url: Optional[str] = None
    title: str
    source: Optional[str] = None
    thumbnail_url: Optional[str] = None
    date: Optional[str] = None
    maker: Optional[str] = None
    label: Optional[str] = None
    series: Optional[str] = None
    sample_image_urls: List[dict] = []
    director: Optional[str] = None
    price: Optional[str] = None
    volume: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class MovieDataOut(BaseModel):
    work_id: str
    prefix: Optional[str] = ""
    title: str
    min_date: Optional[str] = None
    casts: List[dict] = []
    actors: List[dict] = []
    tags: List[dict] = []
    genres: List[str] = []
    created_at: Optional[datetime] = None
    products: List[MovieProductOut] = []

    model_config = {
        "from_attributes": True
    }