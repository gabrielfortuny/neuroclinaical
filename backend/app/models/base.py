"""Base models module that provides common database functionality."""

import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


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
        id (uuid.UUID): Primary key using UUID version 4
        created_at (datetime): Timestamp when the record was created
        updated_at (datetime): Timestamp when the record was last updated
    """

    __abstract__ = True
    id: uuid.UUID = db.Column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    created_at: datetime = db.Column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
