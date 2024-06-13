from uuid import UUID

from sqlmodel import Field

from src.db.mixins import TimeStampWithIdMixin
from src.db.users.models import UsersSQLModel


class UserPassword(UsersSQLModel, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_passwords"
    hashed_password: str = Field(nullable=False)
    user_id: UUID = Field(foreign_key="users.id", index=True)
