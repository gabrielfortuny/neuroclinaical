import uuid
from typing import List, Optional, Union
from datetime import datetime, time
from app import db
from flask import current_app
from sqlalchemy.dialects.postgresql import UUID, INTERVAL
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


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


class BaseModel(db.Model):
    __abstract__ = True
    id: uuid.UUID = db.Column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    created_at: datetime = db.Column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


class FileMixin:
    """Mixin for models that contain file paths."""

    file_name: Optional[str] = db.Column(db.Text)

    @hybrid_property
    def file_path(self) -> str:
        """Returns the physical storage path of the file."""
        return f"{current_app.config['UPLOAD_FOLDER']}/{self.id}"

    @hybrid_property
    def content_type(self) -> str:
        """Derive content type from original filename if available."""
        if self.file_name:
            # Get extension and map to content type
            extension = (
                self.file_name.split(".")[-1].lower()
                if "." in self.file_name
                else None
            )
            if extension is not None:
                content_types = {
                    "pdf": "application/pdf",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    # Add more mappings as needed
                }
                return content_types.get(extension, "application/octet-stream")

        # Default return for cases with no filename or no extension
        return "application/octet-stream"


class User(BaseModel):
    __tablename__ = "users"
    username: str = db.Column(db.Text, nullable=False, unique=True)
    name: str = db.Column(db.Text, nullable=False)
    email: str = db.Column(db.Text, nullable=False, unique=True)
    password_hash: str = db.Column(db.String(128), nullable=False)

    conversations: List["Conversation"] = db.relationship(
        "Conversation", back_populates="user", cascade="all, delete"
    )


class Patient(BaseModel):
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


class Report(BaseModel, FileMixin):
    __tablename__ = "reports"
    patient_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Optional[str] = db.Column(db.Text)

    patient: "Patient" = db.relationship("Patient", back_populates="reports")
    extracted_images: List["ExtractedImage"] = db.relationship(
        "ExtractedImage", back_populates="report", cascade="all, delete"
    )
    seizures: List["Seizure"] = db.relationship(
        "Seizure", back_populates="report", cascade="all, delete"
    )
    drug_administrations: List["DrugAdministration"] = db.relationship(
        "DrugAdministration", back_populates="report", cascade="all, delete"
    )


class ExtractedImage(BaseModel, FileMixin):
    __tablename__ = "extracted_images"
    report_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    report: "Report" = db.relationship(
        "Report", back_populates="extracted_images"
    )


class Seizure(BaseModel):
    __tablename__ = "seizures"
    report_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day: int = db.Column(db.Integer, nullable=False)
    start_time: Optional[time] = db.Column(db.Time)
    duration: Optional[INTERVAL] = db.Column(INTERVAL)

    report: "Report" = db.relationship("Report", back_populates="seizures")
    electrodes: List["Electrode"] = db.relationship(
        "Electrode", secondary=seizures_electrodes, back_populates="seizures"
    )


class Electrode(BaseModel):
    __tablename__ = "electrodes"
    name: str = db.Column(db.Text, nullable=False, index=True)

    seizures: List["Seizure"] = db.relationship(
        "Seizure", secondary=seizures_electrodes, back_populates="electrodes"
    )


class DrugAdministration(BaseModel):
    __tablename__ = "drug_administration"
    report_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    drug_name: str = db.Column(db.Text, nullable=False, index=True)
    day: int = db.Column(db.Integer, nullable=False)
    dosage: int = db.Column(db.Integer, nullable=False)

    report: "Report" = db.relationship(
        "Report", back_populates="drug_administrations"
    )

    __table_args__ = (
        db.CheckConstraint("dosage > 0", name="check_positive_dosage"),
    )


class SupplementalMaterial(BaseModel, FileMixin):
    __tablename__ = "supplemental_materials"
    patient_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    patient: "Patient" = db.relationship(
        "Patient", back_populates="supplemental_materials"
    )


class Conversation(BaseModel):
    __tablename__ = "conversations"
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: "User" = db.relationship("User", back_populates="conversations")
    patient: "Patient" = db.relationship(
        "Patient", back_populates="conversations"
    )
    messages: List["Message"] = db.relationship(
        "Message", back_populates="conversation", cascade="all, delete"
    )


class Message(BaseModel):
    __tablename__ = "messages"
    conversation_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query: str = db.Column(db.Text, nullable=False)
    response: str = db.Column(db.Text, nullable=False)

    conversation: "Conversation" = db.relationship(
        "Conversation", back_populates="messages"
    )
