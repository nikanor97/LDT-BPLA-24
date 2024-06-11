from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.users.models import UsersSQLModel

# if TYPE_CHECKING:
#     from src.db.users.models.user import User


class UserTokenBase(UsersSQLModel):
    access_token: str = Field(nullable=False)
    refresh_token: str = Field(nullable=False)
    token_type: str = Field(nullable=True)
    access_expires_at: datetime = Field(nullable=False)
    refresh_expires_at: datetime = Field(nullable=False)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    is_valid: bool = Field(nullable=False, default=True)


class UserToken(UserTokenBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_tokens"
    user: "User" = Relationship(
        sa_relationship=relationship("User", lazy="selectin"),
        # sa_relationship_kwargs={"lazy": "selectin"}
    )
