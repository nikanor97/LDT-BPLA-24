from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import col

from src.db.exceptions import ResourceAlreadyExists
from src.db.projects.db_manager import DbManager
from src.db.projects.models.label import LabelBase, Label
from src.db.projects.models.project import Project


class LabelDbManager(DbManager):

    @staticmethod
    async def create_labels(
        session: AsyncSession,
        project_id: UUID,
        labels: list[LabelBase]
    ) -> list[Label]:
        await Project.by_id(session, project_id)

        label_names = [lab.name for lab in labels]
        stmt = (
            select(Label)
            .where(Label.project_id == project_id)
            .where(col(Label.name).in_(set(label_names)))
        )
        existing_labels = (await session.execute(stmt)).scalars().all()
        if len(existing_labels) == 0:
            labels_ = []
            for label in labels:
                label_ = Label(
                    name=label.name,
                    description=label.description,
                    color=label.color,
                    project_id=project_id,
                )
                labels_.append(label_)
                session.add(label_)
            # await session.commit()
            return labels_
        else:
            existing_labels_names = [lab.name for lab in existing_labels]
            raise ResourceAlreadyExists(
                f"Labels with names {', '.join(existing_labels_names)} "
                f"already exist in this project. No new labels were created"
            )

    @staticmethod
    async def get_labels_by_project(
        session: AsyncSession,
        project_id: UUID
    ) -> list[Label]:
        await Project.by_id(session, project_id)
        stmt = select(Label).where(Label.project_id == project_id)
        labels = (await session.execute(stmt)).scalars().all()
        return labels
