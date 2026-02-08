"""
Database-backed ChatKit Store — Phase 3 Part 3

Maps ChatKit threads to Conversation model and thread items to Message model.
Uses existing AsyncSessionLocal for all database operations.
"""

import json
import uuid
from datetime import datetime

from chatkit.store import Store, NotFoundError
from chatkit.types import (
    Attachment,
    AssistantMessageContent,
    AssistantMessageItem,
    Page,
    ThreadItem,
    ThreadMetadata,
    UserMessageItem,
    UserMessageTextContent,
)
from sqlmodel import select

from backend.src.database import AsyncSessionLocal
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message


class DatabaseChatKitStore(Store[dict]):
    """
    ChatKit Store backed by Neon PostgreSQL.

    Maps:
    - ChatKit threads → Conversation model
    - ChatKit thread items → Message model
    """

    async def generate_thread_id(self, context: dict) -> str:
        return str(uuid.uuid4())

    def generate_item_id(
        self, item_type: str, thread: ThreadMetadata, context: dict
    ) -> str:
        return str(uuid.uuid4())

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Conversation).where(Conversation.id == thread_id)
            )
            conv = result.scalar_one_or_none()
            if not conv:
                raise NotFoundError(f"Thread {thread_id} not found")
            return self._conv_to_thread(conv)

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Conversation).where(Conversation.id == thread.id)
            )
            conv = result.scalar_one_or_none()
            if conv:
                conv.updated_at = datetime.utcnow()
            else:
                user_id = context.get("user_id", "unknown")
                conv = Conversation(
                    id=thread.id,
                    user_id=user_id,
                    created_at=thread.created_at or datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(conv)
            await session.commit()

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: dict
    ) -> Page[ThreadMetadata]:
        user_id = context.get("user_id")
        async with AsyncSessionLocal() as session:
            query = select(Conversation)
            if user_id:
                query = query.where(Conversation.user_id == user_id)
            if order == "desc":
                query = query.order_by(Conversation.created_at.desc())
            else:
                query = query.order_by(Conversation.created_at.asc())

            result = await session.execute(query)
            all_convs = list(result.scalars().all())

        threads = [self._conv_to_thread(c) for c in all_convs]
        return self._paginate(threads, after, limit, order)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict,
    ) -> Page[ThreadItem]:
        async with AsyncSessionLocal() as session:
            query = (
                select(Message)
                .where(Message.conversation_id == thread_id)
            )
            if order == "desc":
                query = query.order_by(Message.created_at.desc())
            else:
                query = query.order_by(Message.created_at.asc())

            result = await session.execute(query)
            all_msgs = list(result.scalars().all())

        items = [self._msg_to_item(m, thread_id) for m in all_msgs]
        return self._paginate(items, after, limit, order)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict
    ) -> None:
        async with AsyncSessionLocal() as session:
            msg = self._item_to_msg(item, thread_id)
            session.add(msg)
            await session.commit()

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: dict
    ) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Message).where(Message.id == item.id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                content = self._extract_item_text(item)
                if content:
                    existing.content = content
                existing.tool_calls = self._extract_item_tool_calls(item)
            else:
                msg = self._item_to_msg(item, thread_id)
                session.add(msg)
            await session.commit()

    async def load_item(
        self, thread_id: str, item_id: str, context: dict
    ) -> ThreadItem:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Message).where(
                    Message.id == item_id,
                    Message.conversation_id == thread_id,
                )
            )
            msg = result.scalar_one_or_none()
            if not msg:
                raise NotFoundError(
                    f"Item {item_id} not found in thread {thread_id}"
                )
            return self._msg_to_item(msg, thread_id)

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        async with AsyncSessionLocal() as session:
            # Delete messages first
            result = await session.execute(
                select(Message).where(Message.conversation_id == thread_id)
            )
            for msg in result.scalars().all():
                await session.delete(msg)

            result = await session.execute(
                select(Conversation).where(Conversation.id == thread_id)
            )
            conv = result.scalar_one_or_none()
            if conv:
                await session.delete(conv)
            await session.commit()

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict
    ) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Message).where(
                    Message.id == item_id,
                    Message.conversation_id == thread_id,
                )
            )
            msg = result.scalar_one_or_none()
            if msg:
                await session.delete(msg)
                await session.commit()

    async def save_attachment(
        self, attachment: Attachment, context: dict
    ) -> None:
        raise NotImplementedError("Attachments not supported")

    async def load_attachment(
        self, attachment_id: str, context: dict
    ) -> Attachment:
        raise NotImplementedError("Attachments not supported")

    async def delete_attachment(
        self, attachment_id: str, context: dict
    ) -> None:
        raise NotImplementedError("Attachments not supported")

    # --- Conversion helpers ---

    @staticmethod
    def _conv_to_thread(conv: Conversation) -> ThreadMetadata:
        return ThreadMetadata(
            id=conv.id,
            created_at=conv.created_at,
            title=None,
            status="active",
            metadata={},
        )

    @staticmethod
    def _msg_to_item(msg: Message, thread_id: str) -> ThreadItem:
        if msg.role == "user":
            return UserMessageItem(
                id=msg.id,
                thread_id=thread_id,
                created_at=msg.created_at,
                content=[UserMessageTextContent(type="text", text=msg.content)],
            )
        else:
            annotations = []
            if msg.tool_calls:
                try:
                    tool_calls = json.loads(msg.tool_calls)
                    for tc in tool_calls:
                        annotations.append({
                            "type": "tool_call",
                            "tool": tc.get("tool", ""),
                            "arguments": tc.get("arguments", {}),
                        })
                except (json.JSONDecodeError, TypeError):
                    pass
            return AssistantMessageItem(
                id=msg.id,
                thread_id=thread_id,
                created_at=msg.created_at,
                content=[
                    AssistantMessageContent(
                        type="text",
                        text=msg.content,
                        annotations=annotations if annotations else [],
                    )
                ],
            )

    @staticmethod
    def _item_to_msg(item: ThreadItem, thread_id: str) -> Message:
        content = DatabaseChatKitStore._extract_item_text(item)
        tool_calls_json = DatabaseChatKitStore._extract_item_tool_calls(item)

        if isinstance(item, UserMessageItem):
            role = "user"
        else:
            role = "assistant"

        return Message(
            id=item.id,
            conversation_id=thread_id,
            role=role,
            content=content or "",
            tool_calls=tool_calls_json,
            created_at=item.created_at or datetime.utcnow(),
        )

    @staticmethod
    def _extract_item_text(item: ThreadItem) -> str | None:
        if isinstance(item, UserMessageItem):
            texts = []
            for c in item.content:
                if hasattr(c, "text"):
                    texts.append(c.text)
            return " ".join(texts) if texts else None
        elif isinstance(item, AssistantMessageItem):
            texts = []
            for c in item.content:
                if hasattr(c, "text"):
                    texts.append(c.text)
            return " ".join(texts) if texts else None
        return None

    @staticmethod
    def _extract_item_tool_calls(item: ThreadItem) -> str | None:
        if isinstance(item, AssistantMessageItem):
            for c in item.content:
                if hasattr(c, "annotations") and c.annotations:
                    tool_calls = [
                        a for a in c.annotations
                        if isinstance(a, dict) and a.get("type") == "tool_call"
                    ]
                    if tool_calls:
                        return json.dumps(tool_calls)
        return None

    def _paginate(
        self, rows: list, after: str | None, limit: int, order: str
    ) -> Page:
        start = 0
        if after:
            for idx, row in enumerate(rows):
                if row.id == after:
                    start = idx + 1
                    break
        data = rows[start: start + limit]
        has_more = start + limit < len(rows)
        next_after = data[-1].id if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)
