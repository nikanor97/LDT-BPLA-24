from typing import TypeVar

from sqlalchemy.ext.declarative import declarative_base
from src.db.common_sql_model import CommonSqlModel

UsersBase = declarative_base()

user_sqlmodel_T = TypeVar("user_sqlmodel_T", bound="UsersSQLModel")


class UsersSQLModel(CommonSqlModel):
    ...


UsersSQLModel.metadata = UsersBase.metadata  # type: ignore
