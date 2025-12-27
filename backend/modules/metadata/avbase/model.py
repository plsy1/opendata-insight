from pydantic import BaseModel


class Movie(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: list[str]
