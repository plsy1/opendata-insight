from pydantic import BaseModel


class MoviePoster(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: list[str]
