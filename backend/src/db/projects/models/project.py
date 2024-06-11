from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import sqlalchemy
from pydantic import Field
from sqlalchemy import Column
from sqlmodel import Relationship
from sqlalchemy.orm import relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.enums import ProjectStatusOption
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.apartment import Apartment
    from src.db.projects.models.label import Label
    from src.db.projects.models.project_document import ProjectDocument
    from src.db.projects.models.user_role import UserRole
# from sqlalchemy.dialects.postgresql import ENUM as PgEnum


class ProjectBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(nullable=True, default=None)
    status: Optional[ProjectStatusOption] = Field(
        # sa_column=Column(
        #     sqlalchemy.Enum(ProjectStatusOption), default=ProjectStatusOption.created
        # )
        # sa_column=Column(
        #     PgEnum(ProjectStatusOption, name="projectstatusoption", create_type=True),
        #     default=ProjectStatusOption.created
        # ), default=ProjectStatusOption.created
    )
    document_id: Optional[UUID] = Field(nullable=True)  # TODO: Make not Optional
    is_deleted: Optional[bool] = Field(default=False)
    deadline_at: Optional[date] = Field(nullable=True)


class Project(ProjectBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "projects"
    roles: list["UserRole"] = Relationship(
        sa_relationship=relationship(
            'UserRole',
            back_populates="project",
        ),
        # 'UserRole',
        # back_populates="project",
    )
    apartments: list["Apartment"] = Relationship(
        sa_relationship=relationship(
            'Apartment',
            back_populates="project",
        ),
        # 'Apartment',
        # back_populates="project",
    )
    labels: list["Label"] = Relationship(
        sa_relationship=relationship(
            'Label',
            back_populates="project",
        ),
        # 'Label',
        # back_populates="project",
    )
    project_documents: Optional[list["ProjectDocument"]] = Relationship(
        sa_relationship=relationship(
            'ProjectDocument',
            back_populates="project",
        ),
        # 'ProjectDocument',
        # back_populates="project",
    )
