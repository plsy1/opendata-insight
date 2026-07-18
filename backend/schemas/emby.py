from typing import Optional

from pydantic import BaseModel


class EmbyMediaItemOut(BaseModel):
    name: Optional[str] = None
    primary: str
    serverId: Optional[str] = None
    indexLink: str
    playbackLink: Optional[str] = None
    ProductionYear: Optional[int] = None

    model_config = {"extra": "allow"}


class EmbyExistsOut(BaseModel):
    exists: bool
    indexLink: Optional[str] = None

    model_config = {"extra": "allow"}
