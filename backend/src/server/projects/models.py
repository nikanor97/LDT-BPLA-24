import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel
from src.db.projects.models import (
    FrameBase,
    UserRoleBase,
    Project,
    ProjectBase,
    VerificationTag,
    Video,
    VideoBase, VideoStatusOption, Photo, FrameContentTypeOption,
)
from src.db.users.models import User
from src.server.common import ModelWithLabelAndValue


class FrameMarkupReadMassive(BaseModel):
    id: uuid.UUID
    label_id: uuid.UUID
    coord_top_left_x: Decimal
    coord_top_left_y: Decimal
    coord_bottom_right_x: Decimal
    coord_bottom_right_y: Decimal
    confidence: Optional[Decimal]


class FramesWithMarkupRead(FrameBase):
    id: uuid.UUID
    markups: list[FrameMarkupReadMassive]


class ProjectCreateTag(BaseModel):
    tag_id: uuid.UUID
    conf: Optional[Decimal]


class ProjectCreate(ProjectBase):
    tags: list[ProjectCreateTag]


class ProjectWithUsersIds(ProjectBase):
    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime


class BplaProjectStats(BaseModel):
    photo_count: int
    video_count: int
    photo_with_det_count: int
    video_with_det_count: int


class ProjectContentTypeOption(str, enum.Enum):
    photo = "photo"
    video = "video"
    mixed = "mixed"


class ContentTypeOption(str, enum.Enum):
    photo = "photo"
    video = "video"


class ProjectWithUsers(ProjectBase):
    id: uuid.UUID
    author: User
    created_at: datetime
    content_type: ProjectContentTypeOption  # считать основываясь на том что в проекта
    detected_count: int


class ProjectRead(ProjectBase):
    id: uuid.UUID
    tags: list[VerificationTag]
    created_at: datetime
    updated_at: datetime


class VerificationTagWithConfidence(BaseModel):
    id: uuid.UUID
    tagname: str
    groupname: str
    default_confidence: Decimal


class ChangeMarkupsOnFrameNewMarkup(BaseModel):
    label_id: uuid.UUID
    frame_id: uuid.UUID
    coord_top_left_x: Decimal
    coord_top_left_y: Decimal
    coord_bottom_right_x: Decimal
    coord_bottom_right_y: Decimal


class ChangeMarkupsOnFrame(BaseModel):
    content_id: uuid.UUID
    deleted_markups: list[uuid.UUID]
    frame_id: uuid.UUID
    new_markups: list[ChangeMarkupsOnFrameNewMarkup]


class Content(BaseModel):
    project_id: uuid.UUID
    content_type: ContentTypeOption
    height: int
    width: int
    content_id: uuid.UUID
    length_sec: Optional[int]
    n_frames: Optional[int]
    name: str
    owner_id: uuid.UUID
    source_url: str
    status: VideoStatusOption
    detected_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_video(cls, video: Video, detected_count: int = 0):
        return cls(
            project_id=video.project_id,
            content_type=ContentTypeOption.video,
            height=video.height,
            width=video.width,
            content_id=video.id,
            length_sec=video.length_sec,
            n_frames=video.n_frames,
            name=video.name,
            owner_id=video.owner_id,
            source_url=video.source_url,
            status=video.status,
            detected_count=detected_count,
            created_at=video.created_at,
            updated_at=video.updated_at
        )

    @classmethod
    def from_photo(cls, photo: Photo, detected_count: int = 0):
        return cls(
            project_id=photo.project_id,
            content_type=ContentTypeOption.photo,
            height=photo.height,
            width=photo.width,
            content_id=photo.id,
            length_sec=None,
            n_frames=None,
            name=photo.name,
            owner_id=photo.owner_id,
            source_url=photo.source_url,
            status=photo.status,
            detected_count=detected_count,
            created_at=photo.created_at,
            updated_at=photo.updated_at
        )

    @classmethod
    def from_video_or_photo(cls, item: Photo | Video, detected_count: int = 0):
        if isinstance(item, Video):
            return cls.from_video(item, detected_count=detected_count)
        elif isinstance(item, Photo):
            return cls.from_photo(item, detected_count=detected_count)
        else:
            raise ValueError(f"Unexpected item type: {type(item)}")

