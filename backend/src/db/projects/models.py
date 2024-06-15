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


# class ApartmentDecorationTypeOption(str, enum.Enum):
#     rough = "rough"
#     finishing = "finishing"


class RoleTypeOption(str, enum.Enum):
    author = "author"
    view_only = "view_only"
    verificator = "verificator"


class ProjectStatusOption(str, enum.Enum):
    created = "created"  # When project is created by admin
    # in_extraction = "in_extraction"
    # extracted = "extracted"
    # approved = "approved"
    in_progress = "in_progress"  # When verificator started to work at the project
    finished = "finished"  # When the project is totally finished


# class ApartmentStatusOption(str, enum.Enum):
#     created = "created"  # When apartment doesn't have video yet
#     in_progress = (
#         "in_progress"  # When apartment has a video, but it's extraction is not approved
#     )
#     # finished = "finished"  # When apartment's video is approved
#     approved = "approved"
#     declined = "declined"


# class VideoBase(ProjectsDataSQLModel):
#     name: str = Field(nullable=False)
#     description: Optional[str] = Field(nullable=True, default=None)
#     owner_id: uuid.UUID = Field(nullable=False)
#     status: VideoStatusOption = Field(
#         sa_column=Column(
#             sqlalchemy.Enum(VideoStatusOption), default=VideoStatusOption.created
#         )
#     )
#     apartment_id: uuid.UUID = Field(foreign_key="apartments.id", nullable=False)
#
#
# class Video(VideoBase, TimeStampWithIdMixin, table=True):
#     __tablename__ = "videos"
#     frames: Optional[list["Frame"]] = Relationship(
#         back_populates="video",
#     )
#     apartment: "Apartment" = Relationship(
#         back_populates="videos",
#     )
#     # TODO: maybe make these fields non-optional
#     length_sec: Optional[Decimal] = Field(nullable=True)
#     n_frames: Optional[int] = Field(nullable=True)
#     height: Optional[int] = Field(nullable=True)
#     width: Optional[int] = Field(nullable=True)
#     source_url: Optional[str] = Field(nullable=True)


# class ProjectDocumentBase(ProjectsDataSQLModel):
#     source_url: str = Field(nullable=False)
#     project_id: Optional[uuid.UUID] = Field(foreign_key="projects.id", nullable=True)
#     apt_count: Optional[int] = Field(nullable=True)
#     n_finishing: Optional[int] = Field(nullable=True)
#     n_rough: Optional[int] = Field(nullable=True)
#     project_name: Optional[str] = Field(nullable=True)
#     address: Optional[str] = Field(nullable=True)


# class ProjectDocument(ProjectDocumentBase, TimeStampWithIdMixin, table=True):
#     __tablename__ = "project_documents"
#     project: Optional["Project"] = Relationship(
#         back_populates="project_documents",
#     )


# class ApartmentBase(ProjectsDataSQLModel):
#     number: str = Field(nullable=False)
#     decoration_type: Optional[ApartmentDecorationTypeOption] = Field(
#         sa_column=Column(sqlalchemy.Enum(ApartmentDecorationTypeOption), nullable=True)
#     )
#     building: Optional[str] = Field(nullable=True)
#     section: Optional[str] = Field(nullable=True)
#     floor: Optional[int] = Field(nullable=True)
#     rooms_total: Optional[int] = Field(nullable=True)
#     square: Optional[Decimal] = Field(nullable=True)
#     project_id: uuid.UUID = Field(foreign_key="projects.id", nullable=False)
#     status: Optional[ApartmentStatusOption] = Field(
#         sa_column=Column(
#             sqlalchemy.Enum(ApartmentStatusOption),
#             default=ApartmentStatusOption.created,
#         )
#     )
#
#
# class Apartment(ApartmentBase, TimeStampWithIdMixin, table=True):
#     __tablename__ = "apartments"
#     videos: Optional[list["Video"]] = Relationship(
#         back_populates="apartment",
#     )
#     project: "Project" = Relationship(
#         back_populates="apartments",
#     )


# class FrameBase(ProjectsDataSQLModel):
#     video_id: uuid.UUID = Field(foreign_key="videos.id", nullable=False)
#     frame_offset: int = Field(
#         nullable=False,
#         description="Offset in number of frames from the beginning of the video",
#     )
#
#
# class Frame(FrameBase, TimeStampWithIdMixin, table=True):
#     __tablename__ = "frames"
#     __table_args__ = (
#         Index(
#             "idx_frame_video_id_frame_offset", "video_id", "frame_offset", unique=True
#         ),
#     )
#
#     # markups: Optional[list["FrameMarkup"]] = Relationship(
#     #     sa_relationship=relationship(
#     #         "FrameMarkup",
#     #         foreign_keys=['frame_markup.frame_video_id', 'frame_markup.frame_time_point'],
#     #         back_populates="frame"
#     #     )
#     # )
#     markups: Optional[list["FrameMarkup"]] = Relationship(
#         back_populates="frame",
#     )
#     video: Video = Relationship(
#         back_populates="frames",
#     )


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
    # frame_video_id: uuid.UUID = Field(foreign_key="frames.video_id")
    # frame_time_point: Decimal = Field(foreign_key="frames.time_point", )
    frame_id: uuid.UUID = Field(foreign_key="frames.id")
    label_id: uuid.UUID = Field(foreign_key="labels.id")

    coord_top_left_x: Decimal = Field(nullable=True)
    coord_top_left_y: Decimal = Field(nullable=True)
    coord_bottom_right_x: Decimal = Field(nullable=True)
    coord_bottom_right_y: Decimal = Field(nullable=True)

    confidence: Optional[Decimal] = Field(nullable=True)


class FrameMarkup(FrameMarkupBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "frame_markup"
    # __table_args__ = (
    #     ForeignKeyConstraint(
    #         ['frame_video_id', 'frame_time_point'],
    #         ['frames.video_id', 'frames.time_point'],
    #     ),
    # )
    # frame: Frame = Relationship(
    #     sa_relationship=relationship(
    #         Frame, foreign_keys=['frame_video_id', 'frame_time_point'], back_populates="markups"
    #     )
    # )
    frame: "Frame" = Relationship(
        back_populates="markups",
    )
    label: Label = Relationship()


# class ProjectBase(ProjectsDataSQLModel):
#     name: str = Field(nullable=False, index=True)
#     description: Optional[str] = Field(nullable=True, default=None)
#     status: Optional[ProjectStatusOption] = Field(
#         sa_column=Column(
#             sqlalchemy.Enum(ProjectStatusOption), default=ProjectStatusOption.created
#         )
#     )
#     document_id: Optional[uuid.UUID] = Field(nullable=True)  # TODO: Make not Optional
#     is_deleted: Optional[bool] = Field(default=False)
#     deadline_at: Optional[date] = Field(nullable=True)
#
#
# class Project(ProjectBase, TimeStampWithIdMixin, table=True):
#     __tablename__ = "projects"
#     roles: list["UserRole"] = Relationship(
#         back_populates="project",
#     )
#     apartments: list[Apartment] = Relationship(
#         back_populates="project",
#     )
#     labels: list[Label] = Relationship(
#         back_populates="project",
#     )
#     project_documents: Optional[list[ProjectDocument]] = Relationship(
#         back_populates="project",
#     )


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
    # id: uuid.UUID = Field(nullable=False)  # it will be set at the tag create stage (from constants file)


class ProjectTag(ProjectsDataSQLModel, TimeStampWithIdMixin, table=True):
    __tablename__ = "project_tags"
    __table_args__ = (
        UniqueConstraint("project_id", "tag_id", name="project_tag_constr"),
    )
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    tag_id: uuid.UUID = Field(foreign_key="verification_tags.id", index=True)
    tag: VerificationTag = Relationship()
    project: "Project" = Relationship()



# ------------------------------



class ProjectBase(ProjectsDataSQLModel):
    name: str = Field(nullable=False, index=True)
    # description: Optional[str] = Field(nullable=True, default=None)
    status: Optional[ProjectStatusOption] = Field(
        sa_column=Column(
            sqlalchemy.Enum(ProjectStatusOption), default=ProjectStatusOption.created
        )
    )
    # document_id: Optional[uuid.UUID] = Field(nullable=True)  # TODO: Make not Optional
    is_deleted: bool = Field(default=False)
    msg_receiver: Optional[str] = Field(nullable=True)
    # deadline_at: Optional[date] = Field(nullable=True)


class Project(ProjectBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "projects"
    roles: list["UserRole"] = Relationship(
        back_populates="project",
    )
    # apartments: list[Apartment] = Relationship(
    #     back_populates="project",
    # )
    labels: list[Label] = Relationship(
        back_populates="project",
    )
    # project_documents: Optional[list[ProjectDocument]] = Relationship(
    #     back_populates="project",
    # )


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
    # apartment_id: uuid.UUID = Field(foreign_key="apartments.id", nullable=False)


class Video(VideoBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "videos"
    # frames: Optional[list["Frame"]] = Relationship(
    #     back_populates="video",
    # )
    # apartment: "Apartment" = Relationship(
    #     back_populates="videos",
    # )
    # TODO: maybe make these fields non-optional
    length_sec: Optional[Decimal] = Field(nullable=True)
    n_frames: Optional[int] = Field(nullable=True)
    height: Optional[int] = Field(nullable=True)
    width: Optional[int] = Field(nullable=True)
    source_url: Optional[str] = Field(nullable=True)


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


class Photo(PhotoBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "photos"
    height: Optional[int] = Field(nullable=True)
    width: Optional[int] = Field(nullable=True)
    source_url: Optional[str] = Field(nullable=True)
    # frames: Optional["Frame"] = Relationship(
    #     back_populates="photo",
    # )


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
    # __table_args__ = (
    #     Index(
    #         "idx_frame_video_id_frame_offset", "video_id", "frame_offset", unique=True
    #     ),
    # )

    markups: Optional[list["FrameMarkup"]] = Relationship(
        back_populates="frame",
    )
    # video: Video = Relationship(
    #     back_populates="frames",
    # )
