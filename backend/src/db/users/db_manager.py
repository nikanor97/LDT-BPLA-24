# import uuid
# from datetime import datetime
# from typing import Optional
#
# from sqlalchemy.exc import NoResultFound
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlmodel import col
#
# from src.db.base_manager import BaseDbManager
# from src.db.exceptions import ResourceAlreadyExists
# from src.db.users.models import (
#     User,
#     UserBase,
#     UserPassword,
#     UserToken,
#     UserTokenBase,
# )
# from src.server.auth_utils import verify_password, get_password_hash, TokenKind
# from src.db.base_manager import BaseDbManager
#
#
# # TODO: Replace all "create" method with session.add cause otherwise in case
# #  of several creations some objects can be created and others will fail (non-transactional behaviour)
#
# class UsersDbManager(BaseDbManager):
#     pass

# class UsersDbManager(BaseDbManager):
    # async def create_user(self, session: AsyncSession, user: UserBase) -> User:
    #     existing_user = (
    #         await session.execute(select(User).where(User.email == user.email))
    #     ).scalar_one_or_none()
    #     if existing_user is None:
    #         created_user = await User.create(session, user)
    #         return created_user
    #     else:
    #         raise ResourceAlreadyExists(f"User with email {user.email} already exists")
    #
    # async def get_user(
    #     self,
    #     session: AsyncSession,
    #     *,
    #     user_id: Optional[uuid.UUID] = None,
    #     email: Optional[str] = None,
    # ) -> User:
    #     assert (
    #         user_id is not None or email is not None
    #     ), "Either user_id or email should not be None"
    #
    #     user: Optional[User] = None
    #     if user_id is not None:
    #         user = await User.by_id(session, user_id)
    #     elif email is not None:
    #         stmt = select(User).where(User.email == email)
    #         user = (await session.execute(stmt)).scalar_one_or_none()
    #         if user is None:
    #             raise NoResultFound(f"User with email {email} was not found")
    #
    #     assert user is not None
    #     return user
    #
    # async def get_user_or_error(
    #     self,
    #     session: AsyncSession,
    #     user_id: uuid.UUID
    # ) -> User:
    #     return await User.by_id(session, user_id)
    #
    #
    # async def get_users(
    #     self, session: AsyncSession, user_ids: set[uuid.UUID]
    # ) -> list[User]:
    #     stmt = select(User).where(col(User.id).in_(user_ids))
    #     users: list[User] = (await session.execute(stmt)).scalars().all()
    #     wrong_user_ids = set(user_ids) - set([u.id for u in users])
    #     if len(wrong_user_ids) > 0:
    #         raise NoResultFound(
    #             f"Users with ids {wrong_user_ids} were not found in the DB"
    #         )
    #     return users
    #
    # async def get_all_users(self, session: AsyncSession) -> list[User]:
    #     stmt = select(User)
    #     users: list[User] = (await session.execute(stmt)).scalars().all()
    #     return users
    #
    # async def authenticate_user(
    #     self, session: AsyncSession, username: str, password: str
    # ) -> Optional[User]:
    #     stmt = select(User).where(User.email == username)
    #     user: Optional[User] = (await session.execute(stmt)).scalar_one_or_none()
    #     if user is None:
    #         raise NoResultFound(f"User with email {username} does not exist")
    #
    #     stmt = select(UserPassword.hashed_password).where(
    #         UserPassword.user_id == user.id
    #     )
    #     hashed_password: Optional[UserPassword] = (
    #         await session.execute(stmt)
    #     ).scalar_one_or_none()
    #     if hashed_password is None:
    #         raise NoResultFound(f"No hashed password for user with id {user.id} exist")
    #
    #     if not verify_password(password, hashed_password):
    #         return None
    #     return user

    # async def create_user_token(
    #     self, session: AsyncSession, user_token_base: UserTokenBase
    # ) -> UserToken:
    #     await User.by_id(session, user_token_base.user_id)
    #     await self.invalidate_old_tokens(session, user_token_base.user_id)
    #     user_token = await UserToken.create(session, user_token_base)
    #     return user_token

    # async def create_user_password(
    #     self, session: AsyncSession, user_id: uuid.UUID, password: str
    # ) -> bool:
    #     await User.by_id(session, user_id)
    #     hashed_password = get_password_hash(password)
    #     user_password = UserPassword(hashed_password=hashed_password, user_id=user_id)
    #     session.add(user_password)
    #     await session.commit()
    #     return True

    # async def invalidate_old_tokens(
    #     self, session: AsyncSession, user_id: uuid.UUID
    # ) -> None:
    #     """
    #     Invalidates only tokens that have expired refresh one
    #     So it's like a clean-up method for particular user
    #     """
    #     await User.by_id(session, user_id)
    #     stmt = (
    #         select(UserToken)
    #         .where(UserToken.user_id == user_id)
    #         .where(UserToken.is_valid == True)
    #     )
    #     tokens: list[UserToken] = (await session.execute(stmt)).scalars().all()
    #
    #     for token in tokens:
    #         if token.refresh_expires_at <= datetime.now():
    #             token.is_valid = False
    #             session.add(token)

    # async def invalidate_previous_token(
    #     self, session: AsyncSession, refresh_token: str
    # ) -> None:
    #     """
    #     Invalidates previous pair of access and refresh tokens by given refresh token
    #     Should be called in refresh-token method
    #     """
    #     stmt = select(UserToken).where(UserToken.refresh_token == refresh_token)
    #     previous_token: Optional[UserToken] = (
    #         await session.execute(stmt)
    #     ).scalar_one_or_none()
    #     if previous_token is None:
    #         print("ALLERT, refresh token somehow was not found")
    #     else:
    #         previous_token.is_valid = False
    #         session.add(previous_token)

    # async def is_token_valid(
    #     self, session: AsyncSession, token: str, token_kind: TokenKind
    # ) -> bool:
    #     stmt = select(UserToken).where(UserToken.is_valid == True)
    #     if token_kind == TokenKind.access:
    #         stmt = stmt.where(UserToken.access_token == token)
    #     elif token_kind == TokenKind.refresh:
    #         stmt = stmt.where(UserToken.refresh_token == token)
    #     token_from_db: Optional[UserToken] = (
    #         await session.execute(stmt)
    #     ).scalar_one_or_none()
    #
    #     if token_from_db is None:
    #         return False
    #
    #     # I MUST NOT DISABLE A PAIR OF TOKENS IF ACCESS TOKEN IS EXPIRED CAUSE OTHERWISE REFRESH WON'T WORK
    #     if (
    #         token_kind == TokenKind.access
    #         and token_from_db.access_expires_at <= datetime.now()
    #     ):
    #         return False
    #     elif (
    #         token_kind == TokenKind.refresh
    #         and token_from_db.refresh_expires_at <= datetime.now()
    #     ):
    #         token_from_db.is_valid = False
    #         session.add(token_from_db)
    #         await session.commit()
    #         return False
    #     else:
    #         return True
