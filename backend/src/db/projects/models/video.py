from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import sqlalchemy
from sqlmodel import Field
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.enums import VideoStatusOption
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.apartment import Apartment
    from src.db.projects.models.frame import Frame


class VideoBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False)
    description: Optional[str] = Field(nullable=True, default=None)
    owner_id: UUID = Field(nullable=False)
    status: VideoStatusOption = Field(
        sa_column=Column(
            sqlalchemy.Enum(VideoStatusOption), default=VideoStatusOption.created
        ),
        # default=VideoStatusOption.created,
    )
    apartment_id: UUID = Field(foreign_key="apartments.id", nullable=False)


class Video(VideoBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "videos"
    frames: Optional[list["Frame"]] = Relationship(
        # sa_relationship=relationship(
        #     'Frame',
        #     back_populates="video",
        # ),
        back_populates="video",
    )
    apartment: "Apartment" = Relationship(
        # sa_relationship=relationship(
        #     'Apartment',
        #     back_populates="videos",
        # ),
        back_populates="videos",
    )
    # TODO: maybe make these fields non-optional
    length_sec: Optional[Decimal] = Field(nullable=True)
    n_frames: Optional[int] = Field(nullable=True)
    height: Optional[int] = Field(nullable=True)
    width: Optional[int] = Field(nullable=True)
    source_url: Optional[str] = Field(nullable=True)
