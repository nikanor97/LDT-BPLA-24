from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.db.exceptions import ResourceAlreadyExists
from src.db.projects.db_manager import DbManager
from src.db.projects.enums import RoleTypeOption
from src.db.projects.models.project import Project
from src.db.projects.models.user_role import UserRole, UserRoleBase


class UserRoleDbManager(DbManager):

    @staticmethod
    async def get_user_roles(
        session: AsyncSession,
        *,
        user_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        role_type: Optional[RoleTypeOption] = None,
    ) -> list[UserRole]:
        assert (
            user_id is not None or project_id is not None
        ), "Either user_id or project_id should not be None"

        stmt = select(UserRole)

        if user_id is not None:
            # Checking if user with this id exists should be done explicitly
            # await User.by_id(session, user_id)
            stmt = stmt.where(UserRole.user_id == user_id)
        if project_id is not None:
            # Checking if project with this id exists
            await Project.by_id(session, project_id)
            stmt = stmt.where(UserRole.project_id == project_id)
        if role_type is not None:
            stmt = stmt.where(UserRole.role_type == role_type)

        stmt = stmt.options(selectinload(UserRole.project))

        return (await session.execute(stmt)).scalars().all()

    @staticmethod
    async def create_user_role(
        session: AsyncSession,
        user_role: UserRoleBase
    ) -> UserRole:
        # Checking if user with this id exists should be done explicitly

        # Checking if project with this id exists
        await Project.by_id(session, user_role.project_id)

        existing_user_role = (
            await session.execute(
                select(UserRole)
                .where(UserRole.role_type == user_role.role_type)
                .where(UserRole.user_id == user_role.user_id)
                .where(UserRole.project_id == user_role.project_id)
            )
        ).scalar_one_or_none()
        if existing_user_role is None:
            created_user_role = await UserRole.create(session, user_role)
            return created_user_role
        else:
            raise ResourceAlreadyExists(
                f"User role with role_type {user_role.role_type}, "
                f"user_id {user_role.user_id} and "
                f"project_id {user_role.project_id} already exists"
            )
