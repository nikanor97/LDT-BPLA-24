import uuid
from datetime import datetime
from typing import TypeVar

from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Field, Relationship
from src.db.common_sql_model import CommonSqlModel
from src.db.mixins import TimeStampWithIdMixin

UsersBase = declarative_base()

user_sqlmodel_T = TypeVar("user_sqlmodel_T", bound="UsersSQLModel")


class UsersSQLModel(CommonSqlModel):
    ...


UsersSQLModel.metadata = UsersBase.metadata  # type: ignore


class UserBase(UsersSQLModel):
    name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, index=True, unique=True)


class User(UserBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "users"
    # roles: list["UserRole"] = Relationship(
    #     back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    # )


class UserTokenBase(UsersSQLModel):
    access_token: str = Field(nullable=False)
    refresh_token: str = Field(nullable=False)
    token_type: str = Field(nullable=True)
    access_expires_at: datetime = Field(nullable=False)
    refresh_expires_at: datetime = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    is_valid: bool = Field(nullable=False, default=True)


class UserToken(UserTokenBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_tokens"
    user: User = Relationship(sa_relationship_kwargs={"lazy": "selectin"})


class UserPassword(UsersSQLModel, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_passwords"
    hashed_password: str = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
