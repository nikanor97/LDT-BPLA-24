import json
import os
from typing import Any, Callable, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    AsyncSessionTransaction,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker


class SessionAutoBegin:
    def __init__(self, session_maker: sessionmaker) -> None:  # type: ignore
        self._session_maker = session_maker
        self._session: Optional[AsyncSession] = None
        self._transaction: Optional[AsyncSessionTransaction] = None

    async def __aenter__(self) -> AsyncSession:
        session = self._session_maker()
        await session.__aenter__()
        self._session = session

        assert self._session is not None, "mypy stupid check"
        transaction = self._session.begin()
        await transaction.__aenter__()
        self._transaction = transaction

        return session

    async def __aexit__(self, type_: Any, value: Any, traceback: Any) -> None:
        if self._transaction is not None:
            await self._transaction.__aexit__(type_, value, traceback)

        if self._session is not None:
            await self._session.__aexit__(type_, value, traceback)


DbT = TypeVar("DbT", bound="BaseDbManager")


def build_connect_str(
    user: str,
    password: str,
    host: str,
    port: int,
    database_name: str,
) -> str:
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database_name}"


class BaseDbManager:
    def __init__(self, async_engine: AsyncEngine):
        self._engine = async_engine  # used in tests
        self._session_maker = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def make_session(self) -> AsyncSession:
        return self._session_maker()

    def make_autobegin_session(self) -> SessionAutoBegin:
        return SessionAutoBegin(self._session_maker)

    async def close(self) -> None:
        self._session_maker.close_all()  # type: ignore
        await self._engine.dispose()

    @classmethod
    def from_connect_str(
        cls: Type[DbT],
        connect_str: str,
        pool_size: int = 50,
        json_serializer: Optional[Callable[..., str]] = None,
        json_deserializer: Optional[Callable[..., Any]] = None,
    ) -> DbT:
        engine = create_async_engine(
            connect_str,
            pool_size=pool_size,
            future=True,
            pool_pre_ping=True,
            execution_options={"isolation_level": "AUTOCOMMIT"},
            json_serializer=json_serializer or json.dumps,
            json_deserializer=json_deserializer or json.loads,
        )
        return cls(engine)

    @classmethod
    def from_params(
        cls: Type[DbT],
        user: str,
        password: str,
        host: str,
        port: int,
        database_name: str,
        pool_size: int = 50,
        json_serializer: Optional[Callable[..., str]] = None,
        json_deserializer: Optional[Callable[..., Any]] = None,
    ) -> DbT:
        connect_str = build_connect_str(
            user=user,
            password=password,
            host=host,
            port=port,
            database_name=database_name,
        )
        return cls.from_connect_str(
            connect_str=connect_str,
            pool_size=pool_size,
            json_serializer=json_serializer,
            json_deserializer=json_deserializer,
        )


def init_db_manager_closure(
    user: str,
    password: str,
    host: str,
    port: int,
    db_name_prefix: str = "",
    json_serializer: Optional[Callable[..., str]] = None,
    json_deserializer: Optional[Callable[..., Any]] = None,
) -> Callable[[str, Type[DbT], int], DbT]:
    def closure(
        database_name: str,
        db_manager_cls: Type[DbT],
        pool_size: int = 5,
    ) -> DbT:
        return db_manager_cls.from_params(
            user=user,
            password=password,
            host=host,
            port=port,
            database_name=db_name_prefix + database_name,
            pool_size=pool_size,
            json_serializer=json_serializer,
            json_deserializer=json_deserializer,
        )

    return closure


def run_migrations() -> None:
    os.system("alembic upgrade head")
