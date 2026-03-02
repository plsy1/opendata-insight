from pydantic import BaseModel
from typing import Optional
from enum import Enum

VIDEO_RANKING_BASE_URL = "https://video.dmm.co.jp/av/ranking/"


class Actress(BaseModel):
    rank: Optional[str]
    name: Optional[str]
    image: Optional[str]
    profile_url: Optional[str]
    latest_work: Optional[str]
    latest_work_url: Optional[str]
    work_count: int


class Work(BaseModel):
    rank: Optional[str]
    title: Optional[str]
    number: Optional[str]
    image: Optional[str]
    detail_url: Optional[str]
    maker: Optional[str]
    actresses: list[str] = []


class RankingType(Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

    def graphql_filter(self) -> dict:
        """Returns the filter dictionary for the GraphQL query."""
        if self == RankingType.daily:
            return {"daily": {"floor": "AV"}}
        elif self == RankingType.weekly:
            return {"weekly": {"floor": "AV"}}
        else:
            return {"monthly": {"floor": "AV"}}
