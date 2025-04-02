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
