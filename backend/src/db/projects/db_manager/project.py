from collections import defaultdict
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import col

from src.db.projects.db_manager import DbManager
from src.db.projects.enums import RoleTypeOption
from src.db.projects.models.project import ProjectBase, Project
from src.db.projects.models.user_role import UserRole


class ProjectWithUsersIds(ProjectBase):
    id: UUID
    author_id: UUID
    verificators_ids: list[UUID]
    created_at: datetime


class ProjectDbManager(DbManager):

    @staticmethod
    async def get_project(
        session: AsyncSession,
        project_id: UUID
    ) -> Project:
        return await Project.by_id(session, project_id)

    @staticmethod
    async def create_project(
        session: AsyncSession,
        project: ProjectBase,
        user_id: UUID
    ) -> Project:
        # Checking if user with this id exists should be done explicitly

        new_project = Project.parse_obj(project)
        session.add(new_project)

        new_user_role = UserRole(
            user_id=user_id, project_id=new_project.id, role_type=RoleTypeOption.author
        )
        session.add(new_user_role)

        return new_project

    @staticmethod
    async def delete_project(
        session: AsyncSession,
        project_id: UUID
    ) -> Project:
        project = await Project.by_id(session, project_id)
        project.is_deleted = True
        session.add(project)
        return project

    @staticmethod
    async def get_projects_with_users_ids(
        session: AsyncSession,
        user_id: UUID
    ) -> list[ProjectWithUsersIds]:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        user_roles_by_user: list[UserRole] = (
            (await session.execute(stmt)).scalars().all()
        )

        projects_ids = {ur.project_id for ur in user_roles_by_user}

        stmt = select(UserRole).where(col(UserRole.project_id).in_(projects_ids))
        user_roles: list[UserRole] = (await session.execute(stmt)).scalars().all()

        user_roles_by_project_id: defaultdict[UUID, list[UserRole]] = defaultdict(
            list
        )
        for user_role in user_roles:
            user_roles_by_project_id[user_role.project_id].append(user_role)

        stmt = select(Project).where(col(Project.id).in_(projects_ids))
        projects: list[Project] = (await session.execute(stmt)).scalars().all()

        project_by_id: dict[UUID, Project] = dict()
        for project in projects:
            project_by_id[project.id] = project

        projects_with_users_ids: list[ProjectWithUsersIds] = []
        for project_id, usr_rls in user_roles_by_project_id.items():
            # Skipping deleted projects
            if project_by_id[project_id].is_deleted:
                continue
            author_id = None
            verificators_ids = []
            for ur in usr_rls:
                if ur.role_type == RoleTypeOption.author:
                    author_id = ur.user_id
                elif ur.role_type == RoleTypeOption.verificator:
                    verificators_ids.append(ur.user_id)
            project_with_users_ids = ProjectWithUsersIds(
                author_id=author_id,
                verificators_ids=verificators_ids,
                **project_by_id[project_id].dict(),
            )
            projects_with_users_ids.append(project_with_users_ids)

        return projects_with_users_ids

