import json

import settings
from fastapi.encoders import jsonable_encoder
from src.db import init_db_manager_closure
from src.db.projects.db_manager import DbManager as ProjectsDbManager
from src.db.users.db_manager import DbManager as UsersDbManager


class MainDbManager:
    def __init__(self, db_name_prefix: str = "") -> None:
        # by db_name_prefix can rename all databases to test_*
        init_db_manager = init_db_manager_closure(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            db_name_prefix=db_name_prefix,
            json_serializer=lambda obj: json.dumps(jsonable_encoder(obj)),
        )

        self.users = init_db_manager(
            "users",
            UsersDbManager,
            settings.POSTGRES_MAX_CONNECTIONS,
        )

        self.projects = init_db_manager(
            "projects",
            ProjectsDbManager,
            settings.POSTGRES_MAX_CONNECTIONS,
        )

    async def close(self) -> None:
        await self.users.close()
        await self.projects.close()
