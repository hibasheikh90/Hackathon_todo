from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import json
import uuid

from backend.src.models.conversation import Conversation
from backend.src.models.message import Message


class ChatService:
    """Service for managing conversations and messages."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_conversation(
        self, user_id: str, conversation_id: Optional[str] = None
    ) -> Conversation:
        """
        Get an existing conversation or create a new one.

        If conversation_id is provided, fetches it and verifies ownership.
        If not provided, creates a new conversation for the user.
        Raises HTTP 404 if conversation not found or not owned by user.
        """
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                )
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )
            return conversation

        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation_history(self, conversation_id: str) -> list[Message]:
        """
        Load all messages for a conversation ordered by created_at ASC.
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[list[dict]] = None,
    ) -> Message:
        """
        Save a message to the database and update the conversation's updated_at.
        """
        tool_calls_json = json.dumps(tool_calls) if tool_calls else None

        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls_json,
        )
        self.db.add(message)

        # Update conversation's updated_at
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(message)
        return message

    @staticmethod
    def build_input_items(messages: list[Message], max_messages: int = 50) -> list[dict]:
        """
        Convert Message records to OpenAI Agents SDK input format.

        Truncates oldest messages if history exceeds max_messages.
        Returns list of {"role": "user"|"assistant", "content": "..."} dicts.
        """
        if len(messages) > max_messages:
            messages = messages[-max_messages:]

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
