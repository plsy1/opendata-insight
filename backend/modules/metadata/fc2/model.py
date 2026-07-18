from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class RankingType(Enum):
    realtime = "realtime"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class FC2RankingItem(BaseModel):
    term: RankingType
    page: int
    rank: int

    article_id: str
    title: str
    url: HttpUrl
    cover: Optional[HttpUrl] = None
    owner: Optional[str] = None
    seller_id: Optional[str] = None

    rating: int
    comment_count: int
    hot_comments: list[str]


class FC2VideoInformation(BaseModel):
    article_id: Optional[str] = None
    product_id: Optional[str] = None
    cover: Optional[str] = None
    duration: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    seller_id: Optional[str] = None
    sale_day: Optional[str] = None
    sample_images: list[str] = Field(default_factory=list)


class FC2SellerInformation(BaseModel):
    seller_id: str
    author_id: str
    name: str
    profile_url: str
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    short_intro: Optional[str] = None
    description: Optional[str] = None
    product_count: int = 0
    follower_count: int = 0


class FC2SellerWork(BaseModel):
    article_id: str
    title: str
    url: str
    cover: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    rating: int = 0
    comment_count: int = 0
    favorite_count: int = 0
    seller_id: Optional[str] = None
    seller_name: Optional[str] = None


class FC2SellerWorksPage(BaseModel):
    works: list[FC2SellerWork] = Field(default_factory=list)
    page: int = 1
    total: int = 0
    has_next: bool = False
