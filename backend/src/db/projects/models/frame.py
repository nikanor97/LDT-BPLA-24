from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import Field
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.frame_markup import FrameMarkup
    from src.db.projects.models.video import Video


class FrameBase(ProjectsDataSQLModel):
    video_id: UUID = Field(foreign_key="videos.id", nullable=False)
    frame_offset: int = Field(
        nullable=False,
        description="Offset in number of frames from the beginning of the video",
    )


class Frame(FrameBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "frames"
    __table_args__ = (
        Index(
            "idx_frame_video_id_frame_offset", "video_id", "frame_offset", unique=True
        ),
    )

    markups: Optional[list["FrameMarkup"]] = Relationship(
        sa_relationship=relationship(
            "FrameMarkup",
            back_populates="frame",
        )
        # back_populates="frame",
    )
    video: "Video" = Relationship(
        sa_relationship=relationship(
            "Video",
            back_populates="frames",
        )
        # back_populates="frames",
    )
