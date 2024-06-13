from sqlmodel import Field
from src.db.mixins import TimeStampWithIdMixin
from src.db.users.models import UsersSQLModel


class UserBase(UsersSQLModel):
    name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, index=True, unique=True)


class User(UserBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "users"
