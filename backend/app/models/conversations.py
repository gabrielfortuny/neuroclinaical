"""Models for Conversations and Messages within them."""

import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from app import db
from app.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

# avoids circular import
if TYPE_CHECKING:
    from app.models.users import User
    from app.models.patients import Patient


class Conversation(BaseModel):
    """Model representing a conversation with the AI."""

    __tablename__ = "conversations"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="conversations")
    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="conversations"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete"
    )


class Message(BaseModel):
    """Model representing a message within a conversation."""

    __tablename__ = "messages"
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        db.ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query: Mapped[str] = mapped_column(db.Text, nullable=False)
    response: Mapped[str] = mapped_column(db.Text, nullable=False)

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
