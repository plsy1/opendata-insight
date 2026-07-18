from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FC2ProductOut(BaseModel):
    id: int
    article_id: str
    product_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    cover: Optional[str] = None
    duration: Optional[str] = None
    sale_day: Optional[str] = None
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
    rating: Optional[int] = None
    comment_count: Optional[int] = None
    hot_comments: Optional[list[str]] = Field(default_factory=list)
    is_active: Optional[bool] = None
    crawled_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "allow"}
