from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import Field
from sqlalchemy import UniqueConstraint
from sqlmodel import Relationship
from sqlalchemy.orm import relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.project import Project


class LabelBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(nullable=True, default=None)
    color: Optional[str] = Field(nullable=True, default=None)


class Label(LabelBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("name", "project_id", name="name_project_id_constr"),
    )
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    project: "Project" = Relationship(
        sa_relationship=relationship(
            'Project',
            back_populates="labels",
        ),
        # 'Project',
        # back_populates="labels",
    )
