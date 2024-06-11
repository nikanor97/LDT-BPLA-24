from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import col

from src.db.projects.db_manager import DbManager
from src.db.projects.models.project import Project
from src.db.projects.models.project_tag import ProjectTag
from src.db.projects.models.verification_tag import VerificationTag, VerificationTagBase


class VerificationTagDbManager(DbManager):

    @staticmethod
    async def create_verification_tags(
        session: AsyncSession,
        tags: set[VerificationTagBase]
    ) -> list[VerificationTag]:
        # TODO: do it gently with sqlalchemy insert and on_conflict_do_nothing()
        # tags_to_insert = [VerificationTag.parse_obj(tag) for tag in tags]
        # stmt = insert(VerificationTag).values(tags_to_insert).on_conflict_do_nothing()
        # await session.execute(stmt)
        # return tags_to_insert
        existing_tags = await VerificationTagDbManager.get_all_verification_tags(session)
        existing = {(t.tagname, t.groupname) for t in existing_tags}
        tags_to_create: list[VerificationTag] = list()
        for tag in tags:
            if (tag.tagname, tag.groupname) not in existing:
                tags_to_create.append(VerificationTag.parse_obj(tag))
        session.add_all(tags_to_create)
        return tags_to_create

    @staticmethod
    async def get_all_verification_tags(
        session: AsyncSession
    ) -> list[VerificationTag]:
        stmt = select(VerificationTag)
        return (await session.execute(stmt)).scalars().all()

    @staticmethod
    async def get_verification_tags(
        session: AsyncSession, tags_ids: set[UUID]
    ) -> list[VerificationTag]:
        stmt = select(VerificationTag).where(col(VerificationTag.id).in_(tags_ids))
        tags = (await session.execute(stmt)).scalars().all()
        not_existing_tags_ids = set(tags_ids) - set([t.id for t in tags])
        if len(not_existing_tags_ids) != 0:
            raise NoResultFound(
                f"Tags with ids {not_existing_tags_ids} were not found in the DB"
            )
        return tags

    @staticmethod
    async def get_tags_by_project(
        session: AsyncSession,
        project_id: UUID,
    ) -> list[VerificationTag]:
        await Project.by_id(session, project_id)
        stmt = (
            select(ProjectTag)
            .where(ProjectTag.project_id == project_id)
            .options(selectinload(ProjectTag.tag))
        )
        project_tags: list[ProjectTag] = (await session.execute(stmt)).scalars().all()
        tags = [pt.tag for pt in project_tags]

        return tags

