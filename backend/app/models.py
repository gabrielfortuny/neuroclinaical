from flask_sqlalchemy import SQLAlchemy
from app import db  # Import the existing db instance from __init__.py
from sqlalchemy import (
    Table,
    Column,
    Integer,
    Text,
    ForeignKey,
    String,
    Time,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.sql import func

#db = SQLAlchemy()

# Association table: many-to-many between seizures and electrodes
seizures_electrodes = db.Table(
    "seizures_electrodes",
    db.Column(
        "seizure_id",
        db.Integer,
        db.ForeignKey("seizures.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "electrode_id",
        db.Integer,
        db.ForeignKey("electrodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    conversations = db.relationship(
        "Conversation", back_populates="user", cascade="all, delete"
    )


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    reports = db.relationship("Report", back_populates="patient", cascade="all, delete")
    supplemental_materials = db.relationship(
        "SupplementalMaterial", back_populates="patient", cascade="all, delete"
    )
    conversations = db.relationship(
        "Conversation", back_populates="patient", cascade="all, delete"
    )


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    summary = db.Column(db.Text)
    file_path = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="reports")
    extracted_images = db.relationship(
        "ExtractedImage", back_populates="report", cascade="all, delete"
    )
    seizures = db.relationship(
        "Seizure", back_populates="report", cascade="all, delete"
    )
    drug_administrations = db.relationship(
        "DrugAdministration", back_populates="report", cascade="all, delete"
    )


class ExtractedImage(db.Model):
    __tablename__ = "extracted_images"
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(
        db.Integer, db.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    file_path = db.Column(db.Text, nullable=False)

    report = db.relationship("Report", back_populates="extracted_images")


class Seizure(db.Model):
    __tablename__ = "seizures"
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(
        db.Integer, db.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    day = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time)
    duration = db.Column(INTERVAL)

    report = db.relationship("Report", back_populates="seizures")
    electrodes = db.relationship(
        "Electrode", secondary=seizures_electrodes, back_populates="seizures"
    )


class Electrode(db.Model):
    __tablename__ = "electrodes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    seizures = db.relationship(
        "Seizure", secondary=seizures_electrodes, back_populates="electrodes"
    )


class DrugAdministration(db.Model):
    __tablename__ = "drug_administration"
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(
        db.Integer, db.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    drug_name = db.Column(db.Text, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    dosage = db.Column(db.Integer, nullable=False)

    report = db.relationship("Report", back_populates="drug_administrations")


class SupplementalMaterial(db.Model):
    __tablename__ = "supplemental_materials"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    file_path = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="supplemental_materials")


class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )

    user = db.relationship("User", back_populates="conversations")
    patient = db.relationship("Patient", back_populates="conversations")
    messages = db.relationship(
        "Message", back_populates="conversation", cascade="all, delete"
    )


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=func.now())

    conversation = db.relationship("Conversation", back_populates="messages")
