from datetime import datetime
from pydantic import BaseModel, EmailStr
from pydantic.fields import Field
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str
    device_id: str


class User(BaseModel):
    username: str
    tokens: List[Token]
    secret_key: str
    email: EmailStr
    hashed_password: str
    datetime_created: datetime
    is_verified: bool
    roles_id: List[int]