"""
Patient models module.

Patients have a name, reports, supplemental materials, and conversations
associated with them.
"""

from typing import List
from app.models.base import BaseModel, db
from app.models.files import Report, SupplementalMaterial
from app.models.conversations import Conversation


class Patient(BaseModel):
    """
    Model representing a patient.

    Attributes:
        name (str): The patient's full name
        reports (List[Report]): Collection of reports associated with the
            patient
        supplemental_materials (List[SupplementalMaterial]): Additional documents
            related to the patient
        conversations (List[Conversation]): AI-assisted conversations
            regarding the patient
    """

    __tablename__ = "patients"
    name: str = db.Column(db.Text, nullable=False, index=True)

    reports: List["Report"] = db.relationship(
        "Report", back_populates="patient", cascade="all, delete"
    )
    supplemental_materials: List["SupplementalMaterial"] = db.relationship(
        "SupplementalMaterial", back_populates="patient", cascade="all, delete"
    )
    conversations: List["Conversation"] = db.relationship(
        "Conversation", back_populates="patient", cascade="all, delete"
    )
