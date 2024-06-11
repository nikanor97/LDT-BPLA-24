from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.projects.db_manager import DbManager
from src.db.projects.db_manager.verification_tag import VerificationTagDbManager
from src.db.projects.models.project import Project
from src.db.projects.models.project_tag import ProjectTag
from src.db.projects.models.verification_tag import VerificationTag


class ProjectTagDbManager(DbManager):

    @staticmethod
    async def create_project_tags(
        session: AsyncSession,
        project_id: UUID,
        tags_ids: set[UUID]
    ) -> list[ProjectTag]:
        """
        Will add new project tags. If some already exist it'll be OK
        :returns newly created project tags
        """
        await Project.by_id(session, project_id)
        await VerificationTagDbManager.get_verification_tags(session, tags_ids)

        # TODO: implement it with upsert with on conflict update updated_at field only
        stmt = select(ProjectTag.tag_id).where(ProjectTag.project_id == project_id)
        current_project_tags_ids: set[UUID] = set(
            (await session.execute(stmt)).scalars().all()
        )
        new_tags_ids = set(tags_ids) - current_project_tags_ids

        new_project_tags = [
            ProjectTag(project_id=project_id, tag_id=tag_id) for tag_id in new_tags_ids
        ]
        session.add_all(new_project_tags)
        return new_project_tags
