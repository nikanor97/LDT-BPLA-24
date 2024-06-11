from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import col

from src.db.projects.enums import ApartmentStatusOption
from src.db.projects.models.apartment import Apartment
from src.db.projects.models.project import Project
from src.db.projects.models.video import Video


class ProjectsStats(BaseModel):
    total_apartments: int
    total_videos: int
    apartments_approved: int


async def get_all_projects_stats(
        session: AsyncSession,
        user_id: UUID
) -> ProjectsStats:
    projects = await Project.get_projects_with_users_ids(session, user_id)
    projects_ids = {p.id for p in projects}

    stmt = select(Apartment).where(col(Apartment.project_id).in_(projects_ids))
    related_apartments = (await session.execute(stmt)).scalars().all()
    related_apartments_ids = {ra.id for ra in related_apartments}

    stmt = select(Video.apartment_id)
    apartments_ids = (await session.execute(stmt)).scalars().all()

    apartments_ids = set(apartments_ids).intersection(related_apartments_ids)

    n_appartments_approved = sum(
        [
            1
            for a in related_apartments
            if a.status == ApartmentStatusOption.approved
        ]
    )

    stats = ProjectsStats(
        total_apartments=len(related_apartments),
        total_videos=len(apartments_ids),
        apartments_approved=n_appartments_approved,
    )
    return stats
