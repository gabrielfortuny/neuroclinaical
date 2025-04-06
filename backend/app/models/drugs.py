"""Drug administration model."""

from typing import TYPE_CHECKING, Optional
from datetime import time
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app import db
from app.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

# avoids circular import
if TYPE_CHECKING:
    from app.models.files import Report


class DrugAdministration(BaseModel):
    """Model for a drug administration instance."""

    __tablename__ = "drug_administration"
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    drug_name: Mapped[str] = mapped_column(db.Text, nullable=False, index=True)
    day: Mapped[int] = mapped_column(db.Integer, nullable=False)
    dosage: Mapped[int] = mapped_column(db.Integer, nullable=False)
    administration_time: Mapped[Optional[time]] = mapped_column(db.Time)

    report: Mapped["Report"] = relationship(
        "Report", back_populates="drug_administrations"
    )

    __table_args__ = (
        db.CheckConstraint("dosage > 0", name="check_positive_dosage"),
    )
