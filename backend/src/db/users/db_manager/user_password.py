from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.users.db_manager import DbManager
from src.db.users.models.user import User
from src.db.users.models.user_password import UserPassword
from src.server.auth_utils import get_password_hash


class UserPasswordDbManager(DbManager):
    @staticmethod
    async def create_user_password(
        session: AsyncSession,
        user_id: UUID,
        password: str
    ) -> bool:
        await User.by_id(session, user_id)
        hashed_password = get_password_hash(password)
        user_password = UserPassword(hashed_password=hashed_password, user_id=user_id)
        session.add(user_password)
        await session.commit()
        return True
