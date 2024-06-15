from typing import Annotated

from fastapi import Depends, HTTPException
from src.db.main_db_manager import MainDbManager
from src.server.auth_utils import oauth2_scheme, TokenKind


class Auth:
    def __init__(self, main_db_manager: MainDbManager):
        self._main_db_manager = main_db_manager

    async def __call__(self, token: Annotated[str, Depends(oauth2_scheme)]):
        """
        It's impossible to return unified response here, cause Auth is a dependency, so in case of errors
        we should throw an exception
        """
        is_valid = await self.is_access_token_valid(token)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Could not verify credentials")

    async def is_access_token_valid(self, token: str):
        async with self._main_db_manager.users.make_autobegin_session() as session:
            return await self._main_db_manager.users.is_token_valid(
                session, token, TokenKind.access
            )
