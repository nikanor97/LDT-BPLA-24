from typing import Any, Callable, Optional

import loguru
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, ORJSONResponse
from pydantic import ValidationError

from common.rabbitmq.publisher import Publisher
from settings import API_PREFIX  # , AUTH_CLIENT_ID, AUTH_REGION, AUTH_USER_POOL_ID
from src.db.main_db_manager import MainDbManager

# from internal_common.server.cognito_auth_params import CognitoAuthParams
# from internal_common.server.middelwares import AuthorizedRoutesMiddleware
# from internal_common.server.ping_router import PingRouter
from src.server.common import RouterProtocol
from src.server.projects.router import ProjectsRouter
from src.server.users.router import UsersRouter


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    if getattr(exc, "body", None) is not None:
        loguru.logger.error(
            f"incorrect request: detail={exc.errors()}, body: {exc.body}"
        )
        content = {"detail": exc.errors(), "body": exc.body}
    else:
        loguru.logger.error(f"incorrect request: detail={exc.errors()}")
        content = {"detail": exc.errors()}

    return JSONResponse(status_code=422, content=jsonable_encoder(content))


def make_server_app(
    main_db_manager: MainDbManager,
    publisher: Publisher,
    authorization: bool = True,
    startup_events: Optional[list[Callable[[], Any]]] = None,
    shutdown_events: Optional[list[Callable[[], Any]]] = None,
) -> FastAPI:
    """
    ***WARNING

    Currently, the BaseHTTPMiddleware has some known issues:

    It's not possible to use BackgroundTasks with BaseHTTPMiddleware. Check #1438 for more details.
    Using BaseHTTPMiddleware will prevent changes to contextlib.ContextVars from propagating upwards.
    That is, if you set a value for a ContextVar in your endpoint and try to read it from a middleware
    you will find that the value is not the same value you set in your endpoint (see this test for an example of this behavior).
    """
    if startup_events is None:
        startup_events = []

    if shutdown_events is None:
        shutdown_events = []

    app = FastAPI(
        title="API",
        version="0.1",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
        default_response_class=ORJSONResponse,
    )

    # if authorization:
    #     auth_params = CognitoAuthParams(
    #         client_id=AUTH_CLIENT_ID,
    #         user_pool_id=AUTH_USER_POOL_ID,
    #         region=AUTH_REGION,
    #     )
    #
    #     ignore_routes = [
    #         f"{API_PREFIX}/ping",
    #         f"{API_PREFIX}/dcda/slack/message/update",
    #         f"{API_PREFIX}/dcda/slack/command",
    #     ]
    #     auth_middleware = AuthorizedRoutesMiddleware(
    #         auth_params=auth_params,
    #         ignore_routes=ignore_routes,
    #     )
    #     app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
    #     shutdown_events.append(auth_params.close)

    routers_list: list[RouterProtocol] = [
        UsersRouter(main_db_manager=main_db_manager),
        ProjectsRouter(main_db_manager=main_db_manager, publisher=publisher),
    ]
    for router in routers_list:
        # app.include_router(router.router, prefix=API_PREFIX)
        app.include_router(router.router)

    for event in startup_events:
        app.add_event_handler("startup", event)

    for event in shutdown_events:
        app.add_event_handler("shutdown", event)

    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # @app.get("/supply/openapi-camel.json", tags=["Core"], response_class=JSONResponse)
    # async def openapi_camel() -> JSONResponse:
    #     if app.openapi_schema is None:
    #         return JSONResponse({"message": "can not find openapi schema for this application"})
    #     openapi_camel_schema = camel.convert_api_spec_to_camelcase(app.openapi_schema)
    #     return JSONResponse(openapi_camel_schema)

    return app
