class Conversation(BaseModel):
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
