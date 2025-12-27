from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}
