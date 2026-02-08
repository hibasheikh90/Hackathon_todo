from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship
import uuid


if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session owned by a specific user.

    Fields:
    - id: UUID primary key, auto-generated
    - user_id: UUID foreign key linking to User
    - created_at: Timestamp of conversation creation
    - updated_at: Timestamp of last activity
    """
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    messages: list["Message"] = Relationship(back_populates="conversation")
