import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer
from sqlmodel import Field


class TimeStampSqlModelMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
        ),
    )


TimeStampMixin = TimeStampSqlModelMixin


class TimeStampWithIdSqlModelMixin(BaseModel):
    # we don't inheritance from TimeStampMixinRawAlchemy to preserve order
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
        ),
    )


TimeStampWithIdMixin = TimeStampWithIdSqlModelMixin


class TimeStampMixinRawAlchemy:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class TimeStampMixinRawAlchemyWithId:
    # we don't inheritance from TimeStampMixinRawAlchemy to preserve order
    id = Column(Integer, primary_key=True, autoincrement=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
