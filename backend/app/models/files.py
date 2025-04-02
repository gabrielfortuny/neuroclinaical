"""
File handling models.

Includes Report, ExtractedImage, and SupplementalMaterial.
"""

import os
from typing import TYPE_CHECKING, Optional, List
import uuid
from flask import current_app
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

# avoids circular import
if TYPE_CHECKING:
    from app.models.patients import Patient
    from app.models.seizures import Seizure
    from app.models.drugs import DrugAdministration


class FileMixin:
    """
    Mixin for models that contain file paths.

    Attributes:
        file_name (Mapped[Optional[str]]): The original filename of the uploaded
            file
    """

    file_name: Mapped[Optional[str]] = mapped_column(db.Text)

    @hybrid_property
    def file_path(self) -> str:
        """Return the physical storage path of the file."""
        return os.path.join(current_app.config["UPLOAD_FOLDER"], str(self.id))

    @hybrid_property
    def content_type(self) -> str:
        """
        Derive content type from original filename if available.

        Uses the file extension to determine the appropriate MIME type
        for HTTP responses and file handling.

        Returns:
            str: MIME type string corresponding to the file's extension
                 or 'application/octet-stream' if type cannot be determined
        """
        if not self.file_name:
            return "application/octet-stream"

        # Use os.path.splitext to correctly extract the extension
        _, extension = os.path.splitext(self.file_name)

        # Remove the leading dot and convert to lowercase
        if extension:
            extension = extension[1:].lower()

            content_types = {
                "pdf": "application/pdf",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "png": "image/png",
                "txt": "text/plain",
                "doc": "application/msword",
                "docx": "application/vnd.openxmlformats-officedocument.\
                    wordprocessingml.document",
                # Add more mappings as needed
            }
            return content_types.get(extension, "application/octet-stream")

        # Default return for cases with no filename or no extension
        return "application/octet-stream"


class Report(BaseModel, FileMixin):
    """Long term monitoring report for a patient."""

    __tablename__ = "reports"
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[Optional[str]] = mapped_column(db.Text)

    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="reports"
    )
    extracted_images: Mapped[List["ExtractedImage"]] = relationship(
        "ExtractedImage", back_populates="report", cascade="all, delete"
    )
    seizures: Mapped[List["Seizure"]] = relationship(
        "Seizure", back_populates="report", cascade="all, delete"
    )
    drug_administrations: Mapped[List["DrugAdministration"]] = relationship(
        "DrugAdministration", back_populates="report", cascade="all, delete"
    )


class ExtractedImage(BaseModel, FileMixin):
    """Image extracted from a long term monitoring report."""

    __tablename__ = "extracted_images"
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    report: Mapped["Report"] = relationship(
        "Report", back_populates="extracted_images"
    )


class SupplementalMaterial(BaseModel, FileMixin):
    """Supplemental material file related to a patient."""

    __tablename__ = "supplemental_materials"
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="supplemental_materials"
    )
