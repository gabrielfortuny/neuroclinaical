"""Drug administration model."""

from typing import TYPE_CHECKING
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app import db
from app.models.base import BaseModel

# avoids circular import
if TYPE_CHECKING:
    from app.models.files import Report


class DrugAdministration(BaseModel):
    """Model for a drug administration instance."""

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
