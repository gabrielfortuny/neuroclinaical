import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


class BaseModel(db.Model):
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
