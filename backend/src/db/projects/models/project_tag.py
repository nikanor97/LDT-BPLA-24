from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.project import Project
    from src.db.projects.models.verification_tag import VerificationTag


class ProjectTag(ProjectsDataSQLModel, TimeStampWithIdMixin, table=True):
    __tablename__ = "project_tags"
    __table_args__ = (
        UniqueConstraint("project_id", "tag_id", name="project_tag_constr"),
    )
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    tag_id: UUID = Field(foreign_key="verification_tags.id", index=True)
    tag: "VerificationTag" = Relationship(
        # sa_relationship=relationship(
        #     'VerificationTag',
        # ),
    )
    project: "Project" = Relationship(
        # sa_relationship=relationship(
        #     'Project',
        # ),
    )
