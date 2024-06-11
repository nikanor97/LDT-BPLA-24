from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.db.projects.db_manager import DbManager
from src.db.projects.models.frame import Frame
from src.db.projects.models.video import Video


class FrameDbManager(DbManager):

    @staticmethod
    async def get_frame(
        session: AsyncSession,
        frame_id: UUID
    ) -> Frame:
        return await Frame.by_id(session, frame_id)

    @staticmethod
    async def get_frames_by_video(
        session: AsyncSession,
        video_id: UUID
    ) -> list[Frame]:
        await Video.by_id(session, video_id)

        stmt = select(Frame).where(Frame.video_id == video_id)
        frames = (await session.execute(stmt)).scalars().all()
        return frames

    @staticmethod
    async def get_frames_with_markups(
        session: AsyncSession,
        video_id: UUID
    ) -> list[Frame]:
        await Video.by_id(session, video_id)

        stmt = (
            select(Frame)
            .where(Frame.video_id == video_id)
            .options(selectinload(Frame.markups))
        )
        frames = (await session.execute(stmt)).scalars().all()
        return frames

