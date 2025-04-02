"""
Patient models module.

Patients have a name, reports, supplemental materials, and conversations
associated with them.
"""

from typing import TYPE_CHECKING, List
from app import db
from app.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

# avoids circular import
if TYPE_CHECKING:
    from app.models.files import Report, SupplementalMaterial
    from app.models.conversations import Conversation


class Patient(BaseModel):
    """
    Model representing a patient.

    Attributes:
        name (Mapped[str]): The patient's full name
        reports (Mapped[List[Report]]): Collection of reports associated with
            the patient
        supplemental_materials (Mapped[List[SupplementalMaterial]]): Additional
            documents related to the patient
        conversations (Mapped[List[Conversation]]): AI-assisted conversations
            regarding the patient
    """

    __tablename__ = "patients"
    name: Mapped[str] = mapped_column(db.Text, nullable=False, index=True)

    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="patient", cascade="all, delete"
    )
    supplemental_materials: Mapped[List["SupplementalMaterial"]] = (
        relationship(
            "SupplementalMaterial",
            back_populates="patient",
            cascade="all, delete",
        )
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="patient", cascade="all, delete"
    )
