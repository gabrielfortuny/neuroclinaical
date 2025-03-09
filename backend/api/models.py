from datetime import datetime
from sqlalchemy import (Column, Integer, String, Text, ForeignKey, DateTime, Date, Time, Interval, Table)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def current_timestamp():
    return datetime.now(datetime.timezone.utc)

class TimestampMixin:
    created_at = Column(DateTime, default=current_timestamp, nullable=False)
    modified_at = Column(DateTime, default=current_timestamp, onupdate=current_timestamp, nullable=False)

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    conversations = relationship("Conversation", back_populates="user")

class Patient(Base, TimestampMixin):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    dob = Column(Date)
    reports = relationship("Report", back_populates="patient", cascade="all, delete")
    supplemental_materials = relationship("SupplementalMaterial", back_populates="patient", cascade="all, delete")
    seizures = relationship("Seizure", back_populates="patient", cascade="all, delete")
    drug_administrations = relationship("DrugAdministration", back_populates="patient", cascade="all, delete")
    conversations = relationship("Conversation", back_populates="patient")

class Report(Base, TimestampMixin):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    summary = Column(Text)
    filepath = Column(Text, nullable=False)
    patient = relationship("Patient", back_populates="reports")
    extracted_images = relationship("ExtractedImage", back_populates="report", cascade="all, delete")

class ExtractedImage(Base, TimestampMixin):
    __tablename__ = 'extracted_images'
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id', ondelete='CASCADE'), nullable=False)
    filepath = Column(Text, nullable=False)
    report = relationship("Report", back_populates="extracted_images")

class SupplementalMaterial(Base, TimestampMixin):
    __tablename__ = 'supplemental_materials'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    filepath = Column(Text, nullable=False)
    patient = relationship("Patient", back_populates="supplemental_materials")

class Seizure(Base, TimestampMixin):
    __tablename__ = 'seizures'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    day = Column(Integer, nullable=False)
    start_time = Column(Time)
    duration = Column(Interval)
    patient = relationship("Patient", back_populates="seizures")
    electrodes = relationship("Electrode", secondary="seizure_electrode_association", back_populates="seizures")

class Electrode(Base, TimestampMixin):
    __tablename__ = 'electrodes'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    seizures = relationship("Seizure", secondary="seizure_electrode_association", back_populates="electrodes")

seizure_electrode_association = Table(
    'seizure_electrode_association', Base.metadata,
    Column('seizure_id', Integer, ForeignKey('seizures.id', ondelete='CASCADE')),
    Column('electrode_id', Integer, ForeignKey('electrodes.id', ondelete='CASCADE'))
)

class Drug(Base, TimestampMixin):
    __tablename__ = 'drugs'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    drug_class = Column(Text)

class DrugAdministration(Base, TimestampMixin):
    __tablename__ = 'drug_administration'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    drug_id = Column(Integer, ForeignKey('drugs.id', ondelete='CASCADE'), nullable=False)
    day = Column(Integer, nullable=False)
    dosage = Column(Integer, nullable=False)
    patient = relationship("Patient", back_populates="drug_administrations")
    drug = relationship("Drug")

class Conversation(Base, TimestampMixin):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    user = relationship("User", back_populates="conversations")
    patient = relationship("Patient", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete")

class Message(Base, TimestampMixin):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    conversation = relationship("Conversation", back_populates="messages")
