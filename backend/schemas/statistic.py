from pydantic import BaseModel, Field


class StatOverviewOut(BaseModel):
    total: int
    downloaded: int
    not_downloaded: int


class StatDailyOut(BaseModel):
    date: str
    count: int


class StatStudioOut(BaseModel):
    studio: str
    count: int


class StatActorOut(BaseModel):
    actor: str
    count: int


class StatNamedCountOut(BaseModel):
    name: str
    count: int


class StatAllOut(BaseModel):
    overview: StatOverviewOut
    daily: list[StatDailyOut] = Field(default_factory=list)
    studio: list[StatStudioOut] = Field(default_factory=list)
    actors: list[StatActorOut] = Field(default_factory=list)
    makers: list[StatNamedCountOut] = Field(default_factory=list)
    labels: list[StatNamedCountOut] = Field(default_factory=list)
    series: list[StatNamedCountOut] = Field(default_factory=list)
    taxonomy: list[StatNamedCountOut] = Field(default_factory=list)
    genres: list[StatNamedCountOut] = Field(default_factory=list)
    tags: list[StatNamedCountOut] = Field(default_factory=list)
