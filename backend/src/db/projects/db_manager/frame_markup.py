from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import col

from src.db.projects.db_manager import DbManager
from src.db.projects.models.frame import Frame, FrameBase
from src.db.projects.models.frame_markup import FrameMarkup
from src.db.projects.models.label import Label
from src.db.projects.models.video import Video


class MarkupListCreate(BaseModel):
    coord_top_left: tuple[int, int]
    coord_bottom_right: tuple[int, int]
    label_id: UUID
    confidence: Optional[Decimal]


class FramesWithMarkupCreate(BaseModel):
    frame_offset: int
    markup_list: list[MarkupListCreate]


class VideoMarkupCreate(BaseModel):
    video_id: UUID
    frames: list[FramesWithMarkupCreate]


class FrameMarkupDbManager(DbManager):

    @staticmethod
    async def create_frames_with_markups(
        session: AsyncSession,
        video_markup: VideoMarkupCreate
    ) -> list[FrameMarkup]:
        # Checking if video with this id exists
        stmt = (
            select(Video)
            .where(Video.id == video_markup.video_id)
            .options(selectinload(Video.apartment))
        )
        video: Optional[Video] = (await session.execute(stmt)).scalar_one_or_none()
        if video is None:
            raise NoResultFound(f"Video with id {video_markup.video_id} not found")

        # Checking if all provided labels exist
        label_ids = set()
        for frame in video_markup.frames:
            for markup in frame.markup_list:
                label_ids.add(markup.label_id)
        stmt = select(Label.id).where(Label.project_id == video.apartment.project_id)
        available_label_ids = (await session.execute(stmt)).scalars().all()
        not_existing_labels = label_ids - set(available_label_ids)
        if len(not_existing_labels) > 0:
            raise NoResultFound(
                f"Labels with ids {', '.join([str(i) for i in not_existing_labels])} "
                f"do not exist in this project"
            )

        # Creating frames
        desired_frame_offsets = {fr.frame_offset for fr in video_markup.frames}
        stmt = (
            select(Frame.frame_offset)
            .where(Frame.video_id == video_markup.video_id)
            .where(col(Frame.frame_offset).in_(desired_frame_offsets))
        )
        existing_frame_offsets = (await session.execute(stmt)).scalars().all()
        new_frame_offsets = desired_frame_offsets - set(existing_frame_offsets)
        new_frames = []
        for tp in new_frame_offsets:
            new_frame = Frame(video_id=video_markup.video_id, frame_offset=tp)
            new_frames.append(new_frame)
            session.add(new_frame)
        # await session.commit()

        stmt = select(Frame).where(col(Frame.frame_offset).in_(desired_frame_offsets))
        frames: list[Frame] = (await session.execute(stmt)).scalars().all()
        frame_offset_to_frame_id = {fr.frame_offset: fr.id for fr in frames}

        new_markups = []
        for frame in video_markup.frames:
            for markup in frame.markup_list:
                new_markup = FrameMarkup(
                    frame_id=frame_offset_to_frame_id[frame.frame_offset],
                    label_id=markup.label_id,
                    coord_top_left_x=markup.coord_top_left[0],
                    coord_top_left_y=markup.coord_top_left[1],
                    coord_bottom_right_x=markup.coord_bottom_right[0],
                    coord_bottom_right_y=markup.coord_bottom_right[1],
                    confidence=markup.confidence,
                )
                new_markups.append(new_markup)
                session.add(new_markup)

        # await session.commit()
        return new_markups

    @staticmethod
    async def get_frame_markups(
        session: AsyncSession,
        *,
        frame_: Optional[FrameBase] = None,
        frame_id: Optional[UUID] = None,
    ) -> list[FrameMarkup]:
        assert (
            frame_ is not None or frame_id is not None
        ), "Either frame_id or (video_id, frame_offset) should not be None"

        stmt = select(Frame)

        if frame_ is not None:
            # Checking if video with this id exists
            await Video.by_id(session, frame_.video_id)
            stmt = stmt.where(Frame.video_id == frame_.video_id).where(
                Frame.frame_offset == frame_.frame_offset
            )

        if frame_id is not None:
            # Checking if frame with this id exists
            await Frame.by_id(session, frame_id)
            stmt = stmt.where(Frame.id == frame_id)

        stmt = stmt.options(selectinload(Frame.markups))

        frame = (await session.execute(stmt)).scalar_one_or_none()
        if frame is None:
            raise NoResultFound("No frame markups found")
        return frame.markups
