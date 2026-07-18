from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FC2ProductOut(BaseModel):
    id: int
    article_id: str
    product_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    seller_id: Optional[str] = None
    seller_url: Optional[str] = None
    cover: Optional[str] = None
    duration: Optional[str] = None
    sale_day: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    rating: Optional[int] = None
    comment_count: Optional[int] = None
    favorite_count: Optional[int] = None
    seller_page: Optional[int] = None
    seller_position: Optional[int] = None
    sample_images: Optional[list[str]] = Field(default_factory=list)
    crawled_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "allow"}


class FC2RankingOut(BaseModel):
    id: int
    term: str
    article_id: str
    page: Optional[int] = None
    rank: Optional[int] = None
    title: Optional[str] = None
    url: Optional[str] = None
    cover: Optional[str] = None
    owner: Optional[str] = None
    seller_id: Optional[str] = None
    seller_url: Optional[str] = None
    rating: Optional[int] = None
    comment_count: Optional[int] = None
    hot_comments: Optional[list[str]] = Field(default_factory=list)
    is_active: Optional[bool] = None
    crawled_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "allow"}


class FC2SellerOut(BaseModel):
    id: int
    seller_id: str
    author_id: str
    name: str
    profile_url: str
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    short_intro: Optional[str] = None
    description: Optional[str] = None
    product_count: Optional[int] = None
    follower_count: Optional[int] = None
    crawled_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "allow"}


class FC2SellerWorksOut(BaseModel):
    seller: FC2SellerOut
    works: list[FC2ProductOut] = Field(default_factory=list)
    page: int
    total: int
    has_next: bool
