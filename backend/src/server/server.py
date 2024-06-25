from typing import Any, Callable, Optional

import loguru
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, ORJSONResponse
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

import settings
from common.rabbitmq.publisher import Publisher
from settings import API_PREFIX  # , AUTH_CLIENT_ID, AUTH_REGION, AUTH_USER_POOL_ID
from src.db.main_db_manager import MainDbManager

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
        title="API БПЛА",
        version="0.1",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
        default_response_class=ORJSONResponse,
    )

    app.mount("/api/static", StaticFiles(directory=settings.MEDIA_DIR), name="static")

    routers_list: list[RouterProtocol] = [
        UsersRouter(main_db_manager=main_db_manager),
        ProjectsRouter(main_db_manager=main_db_manager, publisher=publisher),
    ]
    for router in routers_list:
        app.include_router(router.router)

    for event in startup_events:
        app.add_event_handler("startup", event)

    for event in shutdown_events:
        app.add_event_handler("shutdown", event)

    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    return app
