from pydantic import BaseModel, Field

from schemas.avbase import MoviePoster
from schemas.movies import MovieDataOut
from schemas.system import SubscriptionQualityRuleConfig


class MovieSubscriptionRulesUpdate(BaseModel):
    use_global: bool = True
    global_excluded_keywords: list[str] = Field(default_factory=list)
    quality_rules: list[SubscriptionQualityRuleConfig] = Field(default_factory=list)


class MovieSubscriptionRulesOut(MovieSubscriptionRulesUpdate):
    pass


class MovieFeedItemOut(MoviePoster):
    """Backward-compatible card fields plus the complete stored movie record."""

    movie: MovieDataOut
    subscription_rules: MovieSubscriptionRulesOut
