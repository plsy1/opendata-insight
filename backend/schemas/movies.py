from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class MovieSubscriptionOut(BaseModel):
    movie_id: int
    is_downloaded: bool
    created_at: Optional[datetime] = None
    rule_config: Optional[dict] = None

    model_config = {"from_attributes": True, "extra": "allow"}


class MovieProductOut(BaseModel):
    id: Optional[int] = None
    work_id: Optional[int] = None
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
    sample_image_urls: List[dict] = Field(default_factory=list)
    director: Optional[str] = None
    price: Optional[str] = None
    volume: Optional[str] = None

    model_config = {"from_attributes": True, "extra": "allow"}

    @field_validator("sample_image_urls", mode="before")
    @classmethod
    def _normalize_sample_images(cls, value):
        return value or []


class MovieDataOut(BaseModel):
    id: Optional[int] = None
    work_id: str
    prefix: Optional[str] = ""
    title: str
    min_date: Optional[str] = None
    casts: List[dict] = Field(default_factory=list)
    actors: List[dict] = Field(default_factory=list)
    tags: List[dict] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    products: List[MovieProductOut] = Field(default_factory=list)
    primary_product: Optional[MovieProductOut] = None
    subscribers: Optional[MovieSubscriptionOut] = None

    model_config = {"from_attributes": True, "extra": "allow"}

    @field_validator("casts", "actors", "tags", "genres", "products", mode="before")
    @classmethod
    def _normalize_lists(cls, value):
        return value or []
