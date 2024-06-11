import settings
from fastapi import APIRouter, Depends
from src.db.main_db_manager import MainDbManager
from src.db.users.models.user import User
from src.server.auth import Auth
from src.server.common import METHOD, UnifiedResponse
from src.server.users.endpoints import UsersEndpoints
from src.server.users.models import Token, TokenWithExpiryData


class UsersRouter:
    def __init__(
        self,
        main_db_manager: MainDbManager,
    ):
        self._users_endpoints = UsersEndpoints(main_db_manager)

        self.router = APIRouter(
            prefix=f"{settings.API_PREFIX}/users",
            tags=["users"],
        )

        self.router.add_api_route(
            path="/user",
            endpoint=self._users_endpoints.create_user,
            response_model=UnifiedResponse[User],
            methods=[METHOD.POST],
        )

        self.router.add_api_route(
            path="/token",
            endpoint=self._users_endpoints.login_for_access_token,
            response_model=UnifiedResponse[TokenWithExpiryData],
            methods=[METHOD.POST],
        )

        self.router.add_api_route(
            path="/swagger-token",
            endpoint=self._users_endpoints.swagger_login_for_access_token,
            response_model=Token,
            methods=[METHOD.POST],
        )

        self.router.add_api_route(
            path="/token-refresh",
            endpoint=self._users_endpoints.refresh_token,
            response_model=UnifiedResponse[TokenWithExpiryData],
            methods=[METHOD.POST],
        )

        self.router.add_api_route(
            path="/me",
            endpoint=self._users_endpoints.get_current_user,
            response_model=UnifiedResponse[User],
            methods=[METHOD.GET],
        )

        self.router.add_api_route(
            path="/users-all",
            endpoint=self._users_endpoints.get_all_users,
            response_model=UnifiedResponse[list[User]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )
