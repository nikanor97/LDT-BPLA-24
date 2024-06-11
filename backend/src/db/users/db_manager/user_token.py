from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.users.db_manager import DbManager
from src.db.users.models.user import User
from src.db.users.models.user_token import UserTokenBase, UserToken
from src.server.auth_utils import TokenKind


class UserTokenDbManager(DbManager):

    @staticmethod
    async def create_user_token(
        session: AsyncSession,
        user_token_base: UserTokenBase
    ) -> UserToken:
        await User.by_id(session, user_token_base.user_id)
        await UserTokenDbManager.invalidate_old_tokens(session, user_token_base.user_id)
        user_token = await UserToken.create(session, user_token_base)
        return user_token

    @staticmethod
    async def invalidate_old_tokens(
        session: AsyncSession,
        user_id: UUID
    ) -> None:
        """
        Invalidates only tokens that have expired refresh one
        So it's like a clean-up method for particular user
        """
        await User.by_id(session, user_id)
        stmt = (
            select(UserToken)
            .where(UserToken.user_id == user_id)
            .where(UserToken.is_valid == True)
        )
        tokens: list[UserToken] = (await session.execute(stmt)).scalars().all()

        for token in tokens:
            if token.refresh_expires_at <= datetime.now():
                token.is_valid = False
                session.add(token)

    @staticmethod
    async def invalidate_previous_token(
        session: AsyncSession,
        refresh_token: str
    ) -> None:
        """
        Invalidates previous pair of access and refresh tokens by given refresh token
        Should be called in refresh-token method
        """
        stmt = select(UserToken).where(UserToken.refresh_token == refresh_token)
        previous_token: Optional[UserToken] = (
            await session.execute(stmt)
        ).scalar_one_or_none()
        if previous_token is None:
            print("ALLERT, refresh token somehow was not found")
        else:
            previous_token.is_valid = False
            session.add(previous_token)

    @staticmethod
    async def is_token_valid(
        session: AsyncSession,
        token: str,
        token_kind: TokenKind
    ) -> bool:
        stmt = select(UserToken).where(UserToken.is_valid == True)
        if token_kind == TokenKind.access:
            stmt = stmt.where(UserToken.access_token == token)
        elif token_kind == TokenKind.refresh:
            stmt = stmt.where(UserToken.refresh_token == token)
        token_from_db: Optional[UserToken] = (
            await session.execute(stmt)
        ).scalar_one_or_none()

        if token_from_db is None:
            return False

        # I MUST NOT DISABLE A PAIR OF TOKENS IF ACCESS TOKEN IS EXPIRED CAUSE OTHERWISE REFRESH WON'T WORK
        if (
            token_kind == TokenKind.access
            and token_from_db.access_expires_at <= datetime.now()
        ):
            return False
        elif (
            token_kind == TokenKind.refresh
            and token_from_db.refresh_expires_at <= datetime.now()
        ):
            token_from_db.is_valid = False
            session.add(token_from_db)
            await session.commit()
            return False
        else:
            return True
