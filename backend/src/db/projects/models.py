import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, TypeVar

import sqlalchemy
from sqlalchemy import Index, UniqueConstraint, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Field, Relationship
from src.db.common_sql_model import CommonSqlModel
from src.db.mixins import TimeStampWithIdMixin

ProjectsDataBase = declarative_base()

projects_sqlmodel_T = TypeVar("projects_sqlmodel_T", bound="ProjectsDataSQLModel")


class ProjectsDataSQLModel(CommonSqlModel):
    ...


ProjectsDataSQLModel.metadata = ProjectsDataBase.metadata  # type: ignore
# TODO: add indexes


class VideoStatusOption(str, enum.Enum):
    created = "created"  # Video is created
    extracted = "extracted"  # Video has gone through extraction
    approved = "approved"  # Video is approved by admin
    declined = "declined"  # Video is declined by admin
    in_progress = "in_progress"  # Video is in progress


class RoleTypeOption(str, enum.Enum):
    author = "author"
    view_only = "view_only"
    verificator = "verificator"


class ProjectStatusOption(str, enum.Enum):
    created = "created"  # When project is created by admin
    in_progress = "in_progress"  # When verificator started to work at the project
    finished = "finished"  # When the project is totally finished


class LabelBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(nullable=True, default=None)
    color: Optional[str] = Field(nullable=True, default=None)


class Label(LabelBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("name", "project_id", name="name_project_id_constr"),
    )
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    project: "Project" = Relationship(
        back_populates="labels",
    )


class FrameMarkupBase(ProjectsDataSQLModel):
    frame_id: uuid.UUID = Field(foreign_key="frames.id")
    label_id: uuid.UUID = Field(foreign_key="labels.id")

    coord_top_left_x: Decimal = Field(nullable=True)
    coord_top_left_y: Decimal = Field(nullable=True)
    coord_bottom_right_x: Decimal = Field(nullable=True)
    coord_bottom_right_y: Decimal = Field(nullable=True)

    confidence: Optional[Decimal] = Field(nullable=True)
    created_by_model: bool = Field(nullable=False, default=True)


class FrameMarkup(FrameMarkupBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "frame_markup"
    frame: "Frame" = Relationship(
        back_populates="markups",
    )
    label: Label = Relationship()


class UserRoleBase(ProjectsDataSQLModel):
    user_id: uuid.UUID = Field(nullable=False, index=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)

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
        back_populates="roles",
    )


class VerificationTagBase(ProjectsDataSQLModel):
    tagname: str = Field(nullable=False)
    groupname: str = Field(nullable=False)


class VerificationTag(VerificationTagBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "verification_tags"
    __table_args__ = (
        Index("idx_tagname_groupname", "tagname", "groupname", unique=True),
    )


class ProjectTag(ProjectsDataSQLModel, TimeStampWithIdMixin, table=True):
    __tablename__ = "project_tags"
    __table_args__ = (
        UniqueConstraint("project_id", "tag_id", name="project_tag_constr"),
    )
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    tag_id: uuid.UUID = Field(foreign_key="verification_tags.id", index=True)
    confidence_threshold: Decimal | None = Field(nullable=True)
    tag: VerificationTag = Relationship()
    project: "Project" = Relationship()


class ProjectBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False, index=True)
    status: Optional[ProjectStatusOption] = Field(
        sa_column=Column(
            sqlalchemy.Enum(ProjectStatusOption), default=ProjectStatusOption.created
        )
    )
    is_deleted: bool = Field(default=False)
    msg_receiver: Optional[str] = Field(nullable=True)


class Project(ProjectBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "projects"
    roles: list["UserRole"] = Relationship(
        back_populates="project",
    )
    labels: list[Label] = Relationship(
        back_populates="project",
    )


class VideoBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False)
    description: Optional[str] = Field(nullable=True, default=None)
    owner_id: uuid.UUID = Field(nullable=False)
    status: VideoStatusOption = Field(
        sa_column=Column(
            sqlalchemy.Enum(VideoStatusOption), default=VideoStatusOption.created
        )
    )
    project_id: Optional[uuid.UUID] = Field(foreign_key="projects.id", nullable=True)
    notification_sent: bool = Field(default=False)


class Video(VideoBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "videos"
    length_sec: Optional[Decimal] = Field(nullable=True)
    n_frames: Optional[int] = Field(nullable=True)
    height: Optional[int] = Field(nullable=True)
    width: Optional[int] = Field(nullable=True)
    source_url: Optional[str] = Field(nullable=True)
    detected_cnt: Optional[int] = Field(nullable=True, default=None)


class PhotoBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False)
    description: Optional[str] = Field(nullable=True, default=None)
    owner_id: uuid.UUID = Field(nullable=False)
    status: VideoStatusOption = Field(
        sa_column=Column(
            sqlalchemy.Enum(VideoStatusOption), default=VideoStatusOption.created
        )
    )
    project_id: Optional[uuid.UUID] = Field(foreign_key="projects.id", nullable=True)
    notification_sent: bool = Field(default=False)


class Photo(PhotoBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "photos"
    height: Optional[int] = Field(nullable=True)
    width: Optional[int] = Field(nullable=True)
    source_url: Optional[str] = Field(nullable=True)
    detected_cnt: Optional[int] = Field(nullable=True, default=None)


class FrameContentTypeOption(str, enum.Enum):
    photo = "photo"
    video = "video"


class FrameBase(ProjectsDataSQLModel):
    content_id: uuid.UUID = Field(nullable=False)
    content_type: FrameContentTypeOption = Field(nullable=False)
    frame_offset: int = Field(
        nullable=False,
        description="Offset in number of frames from the beginning of the video",
    )


class Frame(FrameBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "frames"

    markups: Optional[list["FrameMarkup"]] = Relationship(
        back_populates="frame",
    )
