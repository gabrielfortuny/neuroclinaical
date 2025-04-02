class User(BaseModel):
    __tablename__ = "users"
    username: str = db.Column(db.Text, nullable=False, unique=True)
    name: str = db.Column(db.Text, nullable=False)
    email: str = db.Column(db.Text, nullable=False, unique=True)
    password_hash: str = db.Column(db.String(128), nullable=False)

    conversations: List["Conversation"] = db.relationship(
        "Conversation", back_populates="user", cascade="all, delete"
    )
