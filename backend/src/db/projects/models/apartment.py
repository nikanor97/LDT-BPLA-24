from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import sqlalchemy
from pydantic import Field
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.enums import ApartmentDecorationTypeOption, ApartmentStatusOption
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.video import Video
    from src.db.projects.models.project import Project


class ApartmentBase(ProjectsDataSQLModel):
    number: str = Field(nullable=False)
    decoration_type: Optional[ApartmentDecorationTypeOption] = Field(
        sa_column=Column(sqlalchemy.Enum(ApartmentDecorationTypeOption), nullable=True)
    )
    building: Optional[str] = Field(nullable=True)
    section: Optional[str] = Field(nullable=True)
    floor: Optional[int] = Field(nullable=True)
    rooms_total: Optional[int] = Field(nullable=True)
    square: Optional[Decimal] = Field(nullable=True)
    project_id: UUID = Field(foreign_key="projects.id", nullable=False)
    status: Optional[ApartmentStatusOption] = Field(
        sa_column=Column(
            sqlalchemy.Enum(ApartmentStatusOption),
            default=ApartmentStatusOption.created,
        )
    )


class Apartment(ApartmentBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "apartments"
    videos: Optional[list["Video"]] = Relationship(
        # sa_relationship=relationship(
        #     "Video",
        #     back_populates="apartment",
        # )
        back_populates="apartment",
    )
    project: "Project" = Relationship(
        # sa_relationship=relationship(
        #     "Project",
        #     back_populates="apartments",
        # )
        back_populates="apartments",
    )
