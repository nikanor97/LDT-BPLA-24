from typing import TypeVar

from sqlalchemy.ext.declarative import declarative_base
from src.db.common_sql_model import CommonSqlModel

ProjectsDataBase = declarative_base()

projects_sqlmodel_T = TypeVar("projects_sqlmodel_T", bound="ProjectsDataSQLModel")


class ProjectsDataSQLModel(CommonSqlModel):
    ...


ProjectsDataSQLModel.metadata = ProjectsDataBase.metadata  # type: ignore
# TODO: add indexes
