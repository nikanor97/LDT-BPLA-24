from sqlmodel import Field
from sqlalchemy import Index

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.models import ProjectsDataSQLModel


class VerificationTagBase(ProjectsDataSQLModel):
    tagname: str = Field(nullable=False)
    groupname: str = Field(nullable=False)


class VerificationTag(VerificationTagBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "verification_tags"
    __table_args__ = (
        Index("idx_tagname_groupname", "tagname", "groupname", unique=True),
    )
