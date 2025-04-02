"""Models for Conversations and Messages within them."""

import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from app import db
from app.models.base import BaseModel

# avoids circular import
if TYPE_CHECKING:
    from app.models.users import User
    from app.models.patients import Patient


class Conversation(BaseModel):
    """Model representing a conversation with the AI."""

    __tablename__ = "conversations"
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: "User" = db.relationship("User", back_populates="conversations")
    patient: "Patient" = db.relationship(
        "Patient", back_populates="conversations"
    )
    messages: List["Message"] = db.relationship(
        "Message", back_populates="conversation", cascade="all, delete"
    )


class Message(BaseModel):
    """Model representing a message within a conversation."""

    __tablename__ = "messages"
    conversation_id: uuid.UUID = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query: str = db.Column(db.Text, nullable=False)
    response: str = db.Column(db.Text, nullable=False)

    conversation: "Conversation" = db.relationship(
        "Conversation", back_populates="messages"
    )
