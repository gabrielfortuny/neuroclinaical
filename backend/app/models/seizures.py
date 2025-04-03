"""Seizures and electrode models."""

import uuid
from datetime import time
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy.dialects.postgresql import UUID, INTERVAL
from app import db
from app.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship


# avoids circular import
if TYPE_CHECKING:
    from app.models.files import Report

# Association table: many-to-many between seizures and electrodes
seizures_electrodes = db.Table(
    "seizures_electrodes",
    db.Column(
        "seizure_id",
        UUID(as_uuid=True),
        db.ForeignKey("seizures.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "electrode_id",
        UUID(as_uuid=True),
        db.ForeignKey("electrodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Seizure(BaseModel):
    """Model representing a seizure."""

    __tablename__ = "seizures"
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day: Mapped[int] = mapped_column(db.Integer, nullable=False)
    start_time: Mapped[Optional[time]] = mapped_column(db.Time)
    duration: Mapped[Optional[INTERVAL]] = mapped_column(INTERVAL)

    report: Mapped["Report"] = relationship(
        "Report", back_populates="seizures"
    )
    electrodes: Mapped[List["Electrode"]] = relationship(
        "Electrode", secondary=seizures_electrodes, back_populates="seizures"
    )


class Electrode(BaseModel):
    """Model representing an electrode."""

    __tablename__ = "electrodes"
    name: Mapped[str] = mapped_column(db.Text, nullable=False, index=True)

    seizures: Mapped[List["Seizure"]] = relationship(
        "Seizure", secondary=seizures_electrodes, back_populates="electrodes"
    )
