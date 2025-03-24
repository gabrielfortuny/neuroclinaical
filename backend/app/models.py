from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Date,
    Time,
    Interval,
    Table,
)
from sqlalchemy.orm import relationship
from app import db


def current_timestamp():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(DateTime, default=current_timestamp, nullable=False)
    modified_at = db.Column(
        DateTime, default=current_timestamp, onupdate=current_timestamp, nullable=False
    )


class User(db.Model, TimestampMixin):
    __tablename__ = "users"
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(100), unique=True, nullable=False)
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(100), unique=True, nullable=False)
    password_hash = db.Column(String(128), nullable=False)
    conversations = db.relationship("Conversation", back_populates="user")


class Patient(db.Model, TimestampMixin):
    __tablename__ = "patients"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    dob = db.Column(Date)
    reports = db.relationship("Report", back_populates="patient", cascade="all, delete")
    supplemental_materials = db.relationship(
        "SupplementalMaterial", back_populates="patient", cascade="all, delete"
    )
    seizures = db.relationship(
        "Seizure", back_populates="patient", cascade="all, delete"
    )
    drug_administrations = db.relationship(
        "DrugAdministration", back_populates="patient", cascade="all, delete"
    )
    conversations = db.relationship("Conversation", back_populates="patient")


class Report(db.Model, TimestampMixin):
    __tablename__ = "reports"
    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(
        Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    summary = db.Column(Text)
    filepath = db.Column(Text)
    filetype = db.Column(Text)
    patient = db.relationship("Patient", back_populates="reports")
    extracted_images = db.relationship(
        "ExtractedImage", back_populates="report", cascade="all, delete"
    )
    days = db.Column(Integer, nullable=True)


class ExtractedImage(db.Model, TimestampMixin):
    __tablename__ = "extracted_images"
    id = db.Column(Integer, primary_key=True)
    report_id = db.Column(
        Integer, db.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    filepath = db.Column(Text, nullable=False)
    report = db.relationship("Report", back_populates="extracted_images")


class SupplementalMaterial(db.Model, TimestampMixin):
    __tablename__ = "supplemental_materials"
    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(
        Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    filepath = db.Column(Text, nullable=False)
    patient = db.relationship("Patient", back_populates="supplemental_materials")


class Seizure(db.Model, TimestampMixin):
    __tablename__ = "seizures"
    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(
        Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    day = db.Column(Integer, nullable=False)
    start_time = db.Column(Time)
    duration = db.Column(Integer)
    patient = db.relationship("Patient", back_populates="seizures")
    electrodes = db.relationship(
        "Electrode",
        secondary="seizure_electrode_association",
        back_populates="seizures",
    )


class Electrode(db.Model, TimestampMixin):
    __tablename__ = "electrodes"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(Text, nullable=False)
    seizures = db.relationship(
        "Seizure",
        secondary="seizure_electrode_association",
        back_populates="electrodes",
    )


# Association table for many-to-many relationship
seizure_electrode_association = db.Table(
    "seizure_electrode_association",
    db.Column("seizure_id", Integer, db.ForeignKey("seizures.id", ondelete="CASCADE")),
    db.Column(
        "electrode_id", Integer, db.ForeignKey("electrodes.id", ondelete="CASCADE")
    ),
)


class Drug(db.Model, TimestampMixin):
    __tablename__ = "drugs"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(Text, nullable=False)
    drug_class = db.Column(Text)


class DrugAdministration(db.Model, TimestampMixin):
    __tablename__ = "drug_administration"
    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(
        Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    drug_id = db.Column(
        Integer, db.ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False
    )
    day = db.Column(Integer, nullable=False)
    dosage = db.Column(Integer, nullable=False)
    patient = db.relationship("Patient", back_populates="drug_administrations")
    drug = db.relationship("Drug")
    time = db.Column(Time, nullable=False)


class Conversation(db.Model, TimestampMixin):
    __tablename__ = "conversations"
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(
        Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    patient_id = db.Column(
        Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    user = db.relationship("User", back_populates="conversations")
    patient = db.relationship("Patient", back_populates="conversations")
    messages = db.relationship(
        "Message", back_populates="conversation", cascade="all, delete"
    )


class Message(db.Model, TimestampMixin):
    __tablename__ = "messages"
    id = db.Column(Integer, primary_key=True)
    conversation_id = db.Column(
        Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    query = db.Column(Text, nullable=False)
    response = db.Column(Text, nullable=False)
    conversation = db.relationship("Conversation", back_populates="messages")
