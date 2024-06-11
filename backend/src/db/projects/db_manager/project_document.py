from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.projects.db_manager import DbManager
from src.db.projects.models.project import Project
from src.db.projects.models.project_document import ProjectDocument


class ProjectDocumentDbManager(DbManager):

    @staticmethod
    async def create_project_document(
        session: AsyncSession,
        project_doc: ProjectDocument
    ) -> ProjectDocument:
        if project_doc.project_id is not None:
            await Project.by_id(session, project_doc.project_id)
        project_document = await ProjectDocument.create(session, project_doc)
        return project_document

    @staticmethod
    async def get_project_document(
        session: AsyncSession,
        document_id: UUID
    ) -> ProjectDocument:
        return await ProjectDocument.by_id(session, document_id)
