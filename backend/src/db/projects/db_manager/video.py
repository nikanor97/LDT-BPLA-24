from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.db.projects.db_manager import DbManager
from src.db.projects.db_manager.apartment import ApartmentDbManager
from src.db.projects.enums import VideoStatusOption, ApartmentStatusOption, ProjectStatusOption
from src.db.projects.models.apartment import Apartment
from src.db.projects.models.project import Project
from src.db.projects.models.video import Video


class GpsCoords(BaseModel):
    latitude: Decimal
    longitude: Decimal
    altitude: Decimal


class VideoDbManager(DbManager):

    @staticmethod
    async def create_video(
        session: AsyncSession,
        video: Video
    ) -> Video:
        await Apartment.by_id(session, video.apartment_id)
        return await Video.create(session, video)

    @staticmethod
    async def get_video(
        session: AsyncSession,
        video_id: UUID
    ) -> Video:
        return await Video.by_id(session, video_id)

    @staticmethod
    async def get_videos_by_apartment(
        session: AsyncSession,
        apartment_id: UUID
    ) -> list[Video]:
        await Apartment.by_id(session, apartment_id)
        stmt = (
            select(Apartment)
            .where(Apartment.id == apartment_id)
            .options(selectinload(Apartment.videos))
        )
        apartment: Apartment = (await session.execute(stmt)).scalar()
        return apartment.videos

    @staticmethod
    async def change_video_status(
        session: AsyncSession,
        video_id: UUID,
        new_status: VideoStatusOption
    ) -> Video:
        video = await Video.by_id(session, video_id)
        video.status = new_status
        session.add(video)

        apartment = await Apartment.by_id(session, video.apartment_id)
        project = await Project.by_id(session, apartment.project_id)

        if new_status == VideoStatusOption.declined:
            apartment.status = ApartmentStatusOption.declined

        if new_status in {VideoStatusOption.approved, VideoStatusOption.extracted}:
            if project.status == ProjectStatusOption.created:
                project.status = ProjectStatusOption.in_progress
            if apartment.status == ApartmentStatusOption.created:
                apartment.status = ApartmentStatusOption.in_progress

        if new_status == VideoStatusOption.approved:
            apartment.status = ApartmentStatusOption.approved

            apartments_by_project = await ApartmentDbManager.get_apartments_with_video_by_project(
                session, apartment.project_id
            )
            if all(
                [
                    a.status == ApartmentStatusOption.approved
                    for a in apartments_by_project
                ]
            ):
                project.status = ProjectStatusOption.finished

        session.add(apartment)
        session.add(project)

        return video

    @staticmethod
    async def write_gps_coords(
        session: AsyncSession,
        video_id: UUID,
        gps_coords: GpsCoords
    ) -> "Video":
        video = await Video.by_id(session, video_id)
        video.description = gps_coords.json()
        session.add(video)
        return video
