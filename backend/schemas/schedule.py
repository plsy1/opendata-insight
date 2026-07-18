from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class JobInfoOut(BaseModel):
    id: str
    name: str
    next_run_time: Optional[datetime] = None
    trigger: str
    schedule_type: Literal["interval", "other"]
    interval_seconds: Optional[int] = None
    is_running: bool = False

    model_config = {"from_attributes": True, "extra": "allow"}


class JobRunOut(BaseModel):
    message: str
