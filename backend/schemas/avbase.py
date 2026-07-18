from pydantic import BaseModel, Field


class MoviePoster(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: list[str] = Field(default_factory=list)

    model_config = {"extra": "allow"}


class MovieReleaseGroup(BaseModel):
    maker: str
    works: list[MoviePoster] = Field(default_factory=list)

    model_config = {"extra": "allow"}
