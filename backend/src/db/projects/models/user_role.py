from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy
from sqlmodel import Field
from sqlalchemy import Column, Index
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.models import ProjectsDataSQLModel
from src.db.projects.enums import RoleTypeOption

if TYPE_CHECKING:
    from src.db.projects.models.project import Project


class UserRoleBase(ProjectsDataSQLModel):
    user_id: UUID = Field(nullable=False, index=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True)

    role_type: RoleTypeOption = Field(
        sa_column=Column(sqlalchemy.Enum(RoleTypeOption), nullable=False)
    )


class UserRole(UserRoleBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_roles"
    __table_args__ = (
        Index(
            "idx_user_project_role", "user_id", "project_id", "role_type", unique=True
        ),
    )

    project: "Project" = Relationship(
        # sa_relationship=relationship(
        #     'Project',
        #     back_populates="roles",
        # ),
        back_populates="roles",
    )
