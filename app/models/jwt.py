from datetime import datetime

from pydantic import BaseModel


class JWTUser(BaseModel):
    username: str


class JWTMetadata(BaseModel):
    exp: datetime
    sub: str
