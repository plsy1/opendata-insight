from typing import Literal

from pydantic import BaseModel


class AccessTokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


class TokenVerificationOut(BaseModel):
    valid: bool
    message: str


class MessageOut(BaseModel):
    message: str
