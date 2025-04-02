"""User model with password hashing logic."""

from typing import List, TYPE_CHECKING
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.base import BaseModel

# avoids circular import
if TYPE_CHECKING:
    from app.models.conversations import Conversation


class User(BaseModel):
    """Model representing a user."""

    __tablename__ = "users"
    username: str = db.Column(db.Text, nullable=False, unique=True)
    name: str = db.Column(db.Text, nullable=False)
    email: str = db.Column(db.Text, nullable=False, unique=True)
    password_hash: str = db.Column(db.String(128), nullable=False)

    conversations: List["Conversation"] = db.relationship(
        "Conversation", back_populates="user", cascade="all, delete"
    )

    def set_password(self, password: str) -> None:
        """
        Hash and a new password and updates it in the User's record.

        Args:
            password (str): The provided plaintext password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password_attempt: str) -> bool:
        """
        Check if the provided password hashes to the stored password hash.

        Args:
            password_attempt (str): The plaintext password to be checked.

        Returns:
            bool: True if the password is correct, false otherwise.
        """
        return check_password_hash(self.password_hash, password_attempt)
