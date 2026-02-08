from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship
import uuid


if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Fields:
    - id: UUID primary key, auto-generated
    - conversation_id: FK to conversations table
    - role: "user" or "assistant"
    - content: Message text content
    - tool_calls: JSON string of tool calls (assistant messages only)
    - created_at: Timestamp of message creation
    """
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)
    tool_calls: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    conversation: "Conversation" = Relationship(back_populates="messages")
