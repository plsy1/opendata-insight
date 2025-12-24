from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl


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

    rating: int
    comment_count: int
    hot_comments: list[str]


class FC2VideoInformation(BaseModel):
    cover: Optional[str] = None
    duration: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    sale_day: Optional[str] = None
    product_id: Optional[str] = None
    product_number: Optional[str] = None
    sample_images: list[str] = []
