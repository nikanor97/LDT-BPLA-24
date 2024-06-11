from pydantic import BaseModel

from src.db.users.models.user import UserBase


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenWithExpiryData(Token):
    access_expires_at: int  # n_seconds to expiry
    refresh_expires_at: int  # n_seconds to expiry
