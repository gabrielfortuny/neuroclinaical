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
