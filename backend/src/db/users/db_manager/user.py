from typing import Optional
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import col

from src.db.exceptions import ResourceAlreadyExists
from src.db.users.db_manager import DbManager
from src.db.users.models.user import UserBase, User
from src.db.users.models.user_password import UserPassword
from src.server.auth_utils import verify_password


class UserDbManager(DbManager):

    @staticmethod
    async def create_user(
        session: AsyncSession,
        user: UserBase
    ) -> User:
        existing_user = (
            await session.execute(select(User).where(User.email == user.email))
        ).scalar_one_or_none()
        if existing_user is None:
            created_user = await User.create(session, user)
            return created_user
        else:
            raise ResourceAlreadyExists(f"User with email {user.email} already exists")

    @staticmethod
    async def get_user(
        session: AsyncSession,
        *,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
    ) -> User:
        assert (
            user_id is not None or email is not None
        ), "Either user_id or email should not be None"

        user: Optional[User] = None
        if user_id is not None:
            user = await User.by_id(session, user_id)
        elif email is not None:
            stmt = select(User).where(User.email == email)
            user = (await session.execute(stmt)).scalar_one_or_none()
            if user is None:
                raise NoResultFound(f"User with email {email} was not found")

        assert user is not None
        return user

    @staticmethod
    async def get_user_or_error(
        session: AsyncSession,
        user_id: UUID
    ) -> User:
        return await User.by_id(session, user_id)

    @staticmethod
    async def get_users(
        session: AsyncSession, user_ids: set[UUID]
    ) -> list[User]:
        stmt = select(User).where(col(User.id).in_(user_ids))
        users: list[User] = (await session.execute(stmt)).scalars().all()
        wrong_user_ids = set(user_ids) - set([u.id for u in users])
        if len(wrong_user_ids) > 0:
            raise NoResultFound(
                f"Users with ids {wrong_user_ids} were not found in the DB"
            )
        return users

    @staticmethod
    async def get_all_users(
        session: AsyncSession
    ) -> list[User]:
        stmt = select(User)
        users: list[User] = (await session.execute(stmt)).scalars().all()
        return users

    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        stmt = select(User).where(User.email == username)
        user: Optional[User] = (await session.execute(stmt)).scalar_one_or_none()
        if user is None:
            raise NoResultFound(f"User with email {username} does not exist")

        stmt = select(UserPassword.hashed_password).where(
            UserPassword.user_id == user.id
        )
        hashed_password: Optional[UserPassword] = (
            await session.execute(stmt)
        ).scalar_one_or_none()
        if hashed_password is None:
            raise NoResultFound(f"No hashed password for user with id {user.id} exist")

        if not verify_password(password, hashed_password):
            return None
        return user
