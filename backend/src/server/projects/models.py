import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from src.db.projects.models.apartment import ApartmentBase, Apartment
from src.db.projects.models.frame import FrameBase
from src.db.projects.models.project import Project, ProjectBase
from src.db.projects.models.user_role import UserRoleBase
from src.db.projects.models.verification_tag import VerificationTag
from src.db.projects.models.video import Video
from src.db.users.models.user import User
from src.server.common import ModelWithLabelAndValue


#  TODO: Review all models here


class MarkupListCreate(BaseModel):
    coord_top_left: tuple[int, int]
    coord_bottom_right: tuple[int, int]
    label_id: uuid.UUID
    confidence: Optional[Decimal]


class FramesWithMarkupCreate(BaseModel):
    frame_offset: int
    markup_list: list[MarkupListCreate]


class VideoMarkupCreate(BaseModel):
    video_id: uuid.UUID
    frames: list[FramesWithMarkupCreate]


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


# class VideosWithProjectAssign(BaseModel):
#     video_ids: list[uuid.UUID]
#     project_id: uuid.UUID


class UserRoleWithProjectRead(UserRoleBase):
    id: uuid.UUID
    user: Optional[User]
    project: Optional[Project]


class ProjectCreate(ProjectBase):
    tags_ids: list[uuid.UUID]  # ids of VerificationTags
    verificators_ids: list[
        uuid.UUID
    ]  # ids of verificator users that will be attached to the project


class ProjectRead(ProjectBase):
    id: uuid.UUID
    tags: list[VerificationTag]
    verificators: Optional[list[User]]


# class ProjectWithApartmentsRead(ProjectBase):
#     apartments: list[Apartment]


# class ProjectDocumentStats(BaseModel):
#     project_document_id: uuid.UUID
#     apt_number: int
#     n_finishing: int
#     n_rough: int


# class VerificationTag(BaseModel):
#     tagname: str
#     id: str


# class VerificationTagWithGroup(BaseModel):
#     groupname: str
#     tags: list[VerificationTag]


class GpsCoords(BaseModel):
    latitude: Decimal
    longitude: Decimal
    altitude: Decimal


class ProjectsStats(BaseModel):
    total_apartments: int
    total_videos: int
    apartments_approved: int


class ProjectWithUsersIds(ProjectBase):
    id: uuid.UUID
    author_id: uuid.UUID
    verificators_ids: list[uuid.UUID]
    created_at: datetime


class ProjectWithUsers(ProjectBase):
    id: uuid.UUID
    author: User
    verificators: list[User]
    created_at: datetime


class ApartmentWithVideo(ApartmentBase):
    id: uuid.UUID
    created_at: datetime
    video: Optional[Video]


class ProjectStats(BaseModel):
    total_apartments: int
    total_video_length_minutes: int
    apartments_approved: int


class ScoreMapDecorationTypes(BaseModel):
    no_decor: Decimal
    rough_decor: Decimal
    finishing_decor: Decimal


class ScoreMapItem(BaseModel):
    floor: ScoreMapDecorationTypes
    wall: ScoreMapDecorationTypes
    ceiling: ScoreMapDecorationTypes
    doors_pct: Decimal
    trash_bool: bool
    switch_total: int
    window_decor_pct: Decimal
    radiator_pct: Decimal
    kitchen_total: int
    toilet_pct: Decimal
    bathtub_pct: Decimal
    sink_pct: Decimal
    mop_floor: ScoreMapDecorationTypes
    mop_wall: ScoreMapDecorationTypes
    mop_ceiling: ScoreMapDecorationTypes


class ScoreMapItemDecimal(BaseModel):
    label: str
    value: Decimal


class ScoreMapItemBool(BaseModel):
    label: str
    value: bool


class ScoreMapItemInt(BaseModel):
    label: str
    value: int


class ScoreMapDecorationTypesWithLabels(BaseModel):
    no_decor: ScoreMapItemDecimal
    rough_decor: ScoreMapItemDecimal
    finishing_decor: ScoreMapItemDecimal


class ScoreMapItemWithLabelsMop(BaseModel):
    mop_floor: ModelWithLabelAndValue[ScoreMapDecorationTypesWithLabels]
    mop_wall: ModelWithLabelAndValue[ScoreMapDecorationTypesWithLabels]
    mop_ceiling: ModelWithLabelAndValue[ScoreMapDecorationTypesWithLabels]


class ScoreMapItemWithLabelsNotMop(BaseModel):
    floor: ModelWithLabelAndValue[ScoreMapDecorationTypesWithLabels]
    wall: ModelWithLabelAndValue[ScoreMapDecorationTypesWithLabels]
    ceiling: ModelWithLabelAndValue[ScoreMapDecorationTypesWithLabels]


class ScoreMapItemWithLabelsAllPlaces(BaseModel):
    doors_pct: ScoreMapItemDecimal
    trash_bool: ScoreMapItemBool
    switch_total: ScoreMapItemInt


class ScoreMapItemWithLabelsLifeZones(BaseModel):
    window_decor_pct: ScoreMapItemDecimal
    radiator_pct: ScoreMapItemDecimal
    kitchen_total: ScoreMapItemInt


class ScoreMapItemWithLabelsBathroom(BaseModel):
    toilet_pct: ScoreMapItemDecimal
    bathtub_pct: ScoreMapItemDecimal
    sink_pct: ScoreMapItemDecimal


class ScoreMapItemWithLabels(BaseModel):
    not_mop: ModelWithLabelAndValue[ScoreMapItemWithLabelsNotMop]
    all_places: ModelWithLabelAndValue[ScoreMapItemWithLabelsAllPlaces]
    life_zones: ModelWithLabelAndValue[ScoreMapItemWithLabelsLifeZones]
    bathroom: ModelWithLabelAndValue[ScoreMapItemWithLabelsBathroom]
    mop: ModelWithLabelAndValue[ScoreMapItemWithLabelsMop]


class ProjectScoredOneFloorStat(BaseModel):
    floor: int
    value: Decimal


class ProjectScoresForFloor(BaseModel):
    finishing: list[ProjectScoredOneFloorStat]
    no_decoration: list[ProjectScoredOneFloorStat]


class ProjectScores(BaseModel):
    avg_floor: ScoreMapItem
    for_floor: ProjectScoresForFloor


class ApartmentWithPlans(Apartment):
    apartment_plan_url: Optional[str]
    floor_plan_url: Optional[str]


# class ScoreMap(BaseModel):
#     non_mop_floor_no_percent
#     non_mop_floor_rough_percent
#     non_mop_floor_finishing_percent
#     non_mop_wall_no_percent
#     non_mop_wall_rough_percent
#     non_mop_wall_finishing_percent
#     non_mop_ceiling_no_percent
#     non_mop_ceiling_rough_percent
#     non_mop_ceiling_finishing_percent
#     doors_count
#     garbage
#     switch_count
#     finished_windows_percent
#     batteries_percent
#     kitchen_count
#     toilet_percent
#     bathtub_percent
#     sink_percent
#     mop_floor_no_percent
#     mop_floor_rough_percent
#     mop_floor_finishing_percent
#     mop_wall_no_percent
#     mop_wall_rough_percent
#     mop_wall_finishing_percent
#     mop_ceiling_no_percent
#     mop_ceiling_rough_percent
#     mop_ceiling_finishing_percent
