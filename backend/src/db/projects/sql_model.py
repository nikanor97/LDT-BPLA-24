# import enum
# import uuid
# from datetime import date
# from decimal import Decimal
# from typing import Optional, TypeVar
#
# import sqlalchemy
# from sqlalchemy import Index, UniqueConstraint, Column
# from sqlalchemy.ext.declarative import declarative_base
# from sqlmodel import Field, Relationship
# from src.db.common_sql_model import CommonSqlModel
# from src.db.mixins import TimeStampWithIdMixin
#
# ProjectsDataBase = declarative_base()
#
# projects_sqlmodel_T = TypeVar("projects_sqlmodel_T", bound="ProjectsDataSQLModel")
#
#
# class ProjectsDataSQLModel(CommonSqlModel):
#     ...
#
#
# ProjectsDataSQLModel.metadata = ProjectsDataBase.metadata  # type: ignore
# # TODO: add indexes
