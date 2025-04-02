"""Base models module that provides common database functionality."""

import uuid
from datetime import datetime
from typing import Optional
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column


def generate_uuid() -> uuid.UUID:
    """
    Generate a random UUID.

    Returns:
        uuid.UUID: A newly generated random UUID object
    """
    return uuid.uuid4()


class BaseModel(db.Model):
    """
    Abstract base model that provides common functionality for all models.

    Attributes:
        id (Mapped[uuid.UUID]): Primary key using UUID version 4
        created_at (Mapped[datetime]): Timestamp when the record was created
        updated_at (Mapped[datetime]): Timestamp when the record was last
            updated
    """

    __abstract__ = True
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
