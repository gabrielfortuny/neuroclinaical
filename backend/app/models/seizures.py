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
