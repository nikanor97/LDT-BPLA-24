from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import Field
from sqlalchemy.orm import relationship
from sqlmodel import Relationship

from src.db.mixins import TimeStampWithIdMixin
from src.db.projects.models import ProjectsDataSQLModel

if TYPE_CHECKING:
    from src.db.projects.models.frame import Frame
    from src.db.projects.models.label import Label


class FrameMarkupBase(ProjectsDataSQLModel):
    frame_id: UUID = Field(foreign_key="frames.id")
    label_id: UUID = Field(foreign_key="labels.id")

    coord_top_left_x: Decimal = Field(nullable=True)
    coord_top_left_y: Decimal = Field(nullable=True)
    coord_bottom_right_x: Decimal = Field(nullable=True)
    coord_bottom_right_y: Decimal = Field(nullable=True)

    confidence: Optional[Decimal] = Field(nullable=True)


class FrameMarkup(FrameMarkupBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "frame_markup"
    frame: "Frame" = Relationship(
        sa_relationship=relationship(
            'Frame',
            back_populates="markups",
        ),
        # back_populates="markups",
    )
    label: "Label" = Relationship(
        sa_relationship=relationship(
            'Label',
            # back_populates="markups",
        ),
    )
