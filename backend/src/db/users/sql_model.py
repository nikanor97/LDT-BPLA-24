# import uuid
# from datetime import datetime
# from typing import TypeVar
#
# from sqlalchemy.ext.declarative import declarative_base
# from sqlmodel import Field, Relationship
# from src.db.common_sql_model import CommonSqlModel
# from src.db.mixins import TimeStampWithIdMixin
#
# UsersBase = declarative_base()
#
# user_sqlmodel_T = TypeVar("user_sqlmodel_T", bound="UsersSQLModel")
#
#
# class UsersSQLModel(CommonSqlModel):
#     ...
#
#
# UsersSQLModel.metadata = UsersBase.metadata  # type: ignore
