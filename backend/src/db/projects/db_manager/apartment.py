from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.db.projects.db_manager import DbManager
from src.db.projects.enums import ApartmentStatusOption
from src.db.projects.models.apartment import ApartmentBase, Apartment
from src.db.projects.models.video import Video


class ApartmentWithVideo(ApartmentBase):
    id: UUID
    created_at: datetime
    video: Optional[Video]


class ApartmentDbManager(DbManager):

    @staticmethod
    async def get_apartment(
        session: AsyncSession,
        apartment_id: UUID
    ) -> Apartment:
        return await Apartment.by_id(session, apartment_id)

    @staticmethod
    async def get_apartments_with_video_by_project(
        session: AsyncSession, project_id: UUID
    ) -> list[ApartmentWithVideo]:
        stmt = (
            select(Apartment)
            .where(Apartment.project_id == project_id)
            .options(selectinload(Apartment.videos))
        )
        apartments: list[Apartment] = (await session.execute(stmt)).scalars().all()

        apartments_with_video: list[ApartmentWithVideo] = []
        for idx, apartment in enumerate(apartments):
            video = None
            if len(apartment.videos) > 0:
                video = sorted(apartment.videos, key=lambda x: x.created_at)[-1]
            apartment_with_video = ApartmentWithVideo(video=video, **apartment.dict())
            apartments_with_video.append(apartment_with_video)
        apartments_with_video = sorted(
            apartments_with_video, key=lambda x: x.created_at
        )
        return apartments_with_video

    @staticmethod
    async def change_apartment_status(
        session: AsyncSession,
        apartment_id: UUID,
        new_status: ApartmentStatusOption,
    ) -> Apartment:
        apartment = await Apartment.by_id(session, apartment_id)
        apartment.status = new_status
        session.add(apartment)
        return apartment
