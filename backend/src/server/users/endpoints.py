from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.exc import NoResultFound

from src.db.exceptions import ResourceAlreadyExists
from src.db.main_db_manager import MainDbManager
from src.db.users.models import (
    User,
    UserBase,
)
from src.server.auth_utils import (
    oauth2_scheme,
    get_user_id_from_token,
    create_user_token,
    TokenKind,
)
from src.server.common import UnifiedResponse, exc_to_str
from src.server.users.models import (
    Token,
    TokenWithExpiryData,
    UserCreate,
    UserLogin,
)


class UsersEndpoints:
    def __init__(
        self,
        main_db_manager: MainDbManager,
    ) -> None:
        self._main_db_manager = main_db_manager

    async def create_user(self, user_create: UserCreate) -> UnifiedResponse[User]:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user = UserBase(name=user_create.name, email=user_create.email)
                new_user = await self._main_db_manager.users.create_user(session, user)

                await self._main_db_manager.users.create_user_password(
                    session, new_user.id, user_create.password
                )

                return UnifiedResponse(data=new_user)
            except ResourceAlreadyExists as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=409)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def login_for_access_token(
        self, form_data: UserLogin
    ) -> UnifiedResponse[TokenWithExpiryData]:
        # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user = await self._main_db_manager.users.authenticate_user(
                    session, form_data.username, form_data.password
                )
            except NoResultFound as e:
                # raise HTTPException(status_code=404, detail=exc_to_str(e))
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        if not user:
            # raise HTTPException(
            #     status_code=401,
            #     detail="Incorrect username or password",
            #     headers={"WWW-Authenticate": "Bearer"},
            # )
            return UnifiedResponse(
                error="Incorrect username or password", status_code=401
            )

        user_token_base = create_user_token(user)
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user_token = await self._main_db_manager.users.create_user_token(
                    session, user_token_base
                )
            except NoResultFound as e:
                # raise HTTPException(status_code=404, detail=exc_to_str(e))
                return UnifiedResponse(error=exc_to_str(e), status_code=500)

        # return UnifiedResponse(data=user_token)
        # return {"access_token": access_token, "token_type": "bearer"}
        token = TokenWithExpiryData(
            access_token=user_token.access_token,
            refresh_token=user_token.refresh_token,
            token_type=user_token.token_type,
            access_expires_at=(user_token.access_expires_at - datetime.now()).seconds,
            refresh_expires_at=(user_token.refresh_expires_at - datetime.now()).seconds,
        )
        return UnifiedResponse(data=token)

    async def swagger_login_for_access_token(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
        resp = await self.login_for_access_token(form_data)  # type: ignore
        if resp.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail=resp.error,
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif resp.status_code == 500:
            # SHOULD NEVER COME HERE
            raise HTTPException(
                status_code=500,
                detail="User can not be found, though credentials are correct. It's an internal error.",
            )
        elif resp.status_code == 404:
            raise HTTPException(status_code=404, detail=resp.error)
        elif resp.status_code == 200:
            assert resp.data is not None
            return Token.parse_obj(resp.data)
        else:
            raise HTTPException(
                status_code=500, detail="Unknown status_code. It's an internal error."
            )

    async def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UnifiedResponse[User]:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user_id = get_user_id_from_token(token)
                user = await self._main_db_manager.users.get_user(
                    session, user_id=user_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
            except JWTError as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=401)
        return UnifiedResponse(data=user)

    async def refresh_token(
        self, refresh_token: str
    ) -> UnifiedResponse[TokenWithExpiryData]:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            is_valid = await self._main_db_manager.users.is_token_valid(
                session, refresh_token, token_kind=TokenKind.refresh
            )
            if not is_valid:
                return UnifiedResponse(
                    error="Refresh token has expired", status_code=401
                )

            user_id = get_user_id_from_token(refresh_token)

            user = await self._main_db_manager.users.get_user(session, user_id=user_id)

            user_token_base = create_user_token(user)

            new_user_token = await self._main_db_manager.users.create_user_token(
                session, user_token_base
            )

            await self._main_db_manager.users.invalidate_previous_token(
                session, refresh_token
            )

        token = TokenWithExpiryData(
            access_token=new_user_token.access_token,
            refresh_token=new_user_token.refresh_token,
            token_type=new_user_token.token_type,
            access_expires_at=(
                new_user_token.access_expires_at - datetime.now()
            ).seconds,
            refresh_expires_at=(
                new_user_token.refresh_expires_at - datetime.now()
            ).seconds,
        )
        return UnifiedResponse(data=token)

    async def get_all_users(self) -> UnifiedResponse[list[User]]:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_all_users(session)
        return UnifiedResponse(data=users)
