from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.project import Project


class ProjectDocumentBase(ProjectsDataSQLModel):
    source_url: str = Field(nullable=False)
    project_id: Optional[UUID] = Field(foreign_key="projects.id", nullable=True)
    apt_count: Optional[int] = Field(nullable=True)
    n_finishing: Optional[int] = Field(nullable=True)
    n_rough: Optional[int] = Field(nullable=True)
    project_name: Optional[str] = Field(nullable=True)
    address: Optional[str] = Field(nullable=True)


class ProjectDocument(ProjectDocumentBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "project_documents"
    project: Optional["Project"] = Relationship(
        # sa_relationship=relationship(
        #     "Project",
        #     back_populates="project_documents",
        # )
        back_populates="project_documents",
    )
