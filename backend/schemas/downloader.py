from typing import Literal, Optional

from pydantic import BaseModel
from schemas.fc2 import FC2ProductOut
from schemas.movies import MovieDataOut


class DownloadingTorrentOut(BaseModel):
    hash: str
    name: str
    progress: float
    size: int
    download_speed: int
    eta: int
    tags: str
    work_id: Optional[str] = None
    media_type: Optional[Literal["jav", "fc2"]] = None
    movie: Optional[MovieDataOut] = None
    fc2_product: Optional[FC2ProductOut] = None

    model_config = {"extra": "allow"}


class DeleteTorrentOut(BaseModel):
    status: Literal["success"]
    hash: str
    deleted_files: bool

    model_config = {"extra": "allow"}
