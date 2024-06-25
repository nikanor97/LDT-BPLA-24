import uuid
from typing import Any, Sequence, TypeVar, Union

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import SQLModel

sqlmodel_T = TypeVar("sqlmodel_T", bound=SQLModel)


class CommonSqlModel(SQLModel):
    @classmethod
    async def by_id(
        cls: type[sqlmodel_T], session: AsyncSession, id_: Union[uuid.UUID, int]
    ) -> sqlmodel_T:
        obj = await session.get(cls, id_)
        if obj is None:
            raise NoResultFound(f"{cls.__name__} with id {id_} not found")
        return obj

    @classmethod
    async def all(cls: type[sqlmodel_T], session: AsyncSession) -> list[sqlmodel_T]:
        res = await session.execute(select(cls))
        return res.scalars().all()

    @classmethod
    async def create(
        cls: type[sqlmodel_T],
        session: AsyncSession,
        source: Union[dict[Any, Any], SQLModel],
    ) -> sqlmodel_T:
        if isinstance(source, SQLModel) or isinstance(source, dict):
            obj = cls.parse_obj(source)
        else:
            raise ValueError(f"The input type {type(source)} can not be processed")

        session.add(obj)
        # await session.commit()  # session.flush()

        return obj  # type: ignore

    @classmethod
    async def create_multiple(
        cls: type[sqlmodel_T],
        session: AsyncSession,
        sources: Sequence[Union[dict[Any, Any], SQLModel]],
    ) -> None:
        for source in sources:
            obj: sqlmodel_T
            if isinstance(source, SQLModel):
                obj = cls.from_orm(source)
            elif isinstance(source, dict):
                obj = cls.parse_obj(source)
            else:
                raise ValueError(f"The input type {type(source)} can not be processed")

            session.add(obj)

        await session.commit()
