"""
Tests for Conversation and Message models.

Tests CRUD operations, user isolation, and message ordering
using a real database connection.
"""

import json
import sys
import types
import uuid
from pathlib import Path

import pytest
import pytest_asyncio

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# Module aliasing — prevent duplicate SQLAlchemy table registration.
# ---------------------------------------------------------------------------
import src.models
import src.models.task
import src.models.user
import src.models.conversation
import src.models.message

if "backend" not in sys.modules:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(Path(__file__).parent.parent)]
    sys.modules["backend"] = backend_pkg
if "backend.src" not in sys.modules:
    backend_src_pkg = types.ModuleType("backend.src")
    backend_src_pkg.__path__ = [str(Path(__file__).parent.parent / "src")]
    sys.modules["backend.src"] = backend_src_pkg

sys.modules["backend.src.models"] = src.models
sys.modules["backend.src.models.task"] = src.models.task
sys.modules["backend.src.models.user"] = src.models.user
sys.modules["backend.src.models.conversation"] = src.models.conversation
sys.modules["backend.src.models.message"] = src.models.message

import src.database
sys.modules["backend.src.database"] = src.database

from src.database import AsyncSessionLocal
from src.models.conversation import Conversation
from src.models.message import Message

pytestmark = pytest.mark.asyncio(loop_scope="session")

TEST_USER = f"conv-test-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(autouse=True, scope="session", loop_scope="session")
async def manage_test_user():
    """Create test user at start, clean up at end."""
    from sqlalchemy import text

    # Ensure tables exist
    from src.database import async_engine
    from sqlmodel import SQLModel
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                "INSERT INTO users (id, email, password_hash, is_active, created_at, updated_at) "
                "VALUES (:id, :email, :pw, true, NOW(), NOW()) "
                "ON CONFLICT (id) DO NOTHING"
            ),
            {"id": TEST_USER, "email": f"{TEST_USER}@test.com", "pw": "testhash"},
        )
        await session.commit()

    yield

    async with AsyncSessionLocal() as session:
        await session.execute(
            text("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :uid)"),
            {"uid": TEST_USER},
        )
        await session.execute(
            text("DELETE FROM conversations WHERE user_id = :uid"),
            {"uid": TEST_USER},
        )
        await session.execute(
            text("DELETE FROM users WHERE id = :uid"),
            {"uid": TEST_USER},
        )
        await session.commit()


# ---------------------------------------------------------------------------
# Tests — Conversation CRUD
# ---------------------------------------------------------------------------

class TestConversationCRUD:
    async def test_create_conversation(self):
        async with AsyncSessionLocal() as session:
            conv = Conversation(
                id=str(uuid.uuid4()),
                user_id=TEST_USER,
            )
            session.add(conv)
            await session.commit()
            await session.refresh(conv)

            assert conv.id is not None
            assert conv.user_id == TEST_USER
            assert conv.created_at is not None
            assert conv.updated_at is not None

    async def test_query_conversation_by_user(self):
        async with AsyncSessionLocal() as session:
            conv = Conversation(id=str(uuid.uuid4()), user_id=TEST_USER)
            session.add(conv)
            await session.commit()

            from sqlmodel import select
            result = await session.execute(
                select(Conversation).where(
                    Conversation.user_id == TEST_USER,
                    Conversation.id == conv.id,
                )
            )
            found = result.scalar_one_or_none()
            assert found is not None
            assert found.id == conv.id

    async def test_query_conversation_wrong_user_returns_none(self):
        async with AsyncSessionLocal() as session:
            conv = Conversation(id=str(uuid.uuid4()), user_id=TEST_USER)
            session.add(conv)
            await session.commit()

            from sqlmodel import select
            result = await session.execute(
                select(Conversation).where(
                    Conversation.user_id == "wrong-user-id",
                    Conversation.id == conv.id,
                )
            )
            found = result.scalar_one_or_none()
            assert found is None


# ---------------------------------------------------------------------------
# Tests — Message CRUD
# ---------------------------------------------------------------------------

class TestMessageCRUD:
    async def test_create_message(self):
        async with AsyncSessionLocal() as session:
            conv = Conversation(id=str(uuid.uuid4()), user_id=TEST_USER)
            session.add(conv)
            await session.commit()

            msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conv.id,
                role="user",
                content="Hello, world!",
            )
            session.add(msg)
            await session.commit()
            await session.refresh(msg)

            assert msg.id is not None
            assert msg.role == "user"
            assert msg.content == "Hello, world!"
            assert msg.tool_calls is None
            assert msg.created_at is not None

    async def test_message_with_tool_calls(self):
        async with AsyncSessionLocal() as session:
            conv = Conversation(id=str(uuid.uuid4()), user_id=TEST_USER)
            session.add(conv)
            await session.commit()

            tool_calls = json.dumps([{"tool": "list_tasks", "arguments": {"user_id": TEST_USER}}])
            msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conv.id,
                role="assistant",
                content="Here are your tasks.",
                tool_calls=tool_calls,
            )
            session.add(msg)
            await session.commit()
            await session.refresh(msg)

            parsed = json.loads(msg.tool_calls)
            assert len(parsed) == 1
            assert parsed[0]["tool"] == "list_tasks"

    async def test_messages_ordered_by_created_at(self):
        import asyncio
        async with AsyncSessionLocal() as session:
            conv = Conversation(id=str(uuid.uuid4()), user_id=TEST_USER)
            session.add(conv)
            await session.commit()

            for i in range(3):
                msg = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conv.id,
                    role="user" if i % 2 == 0 else "assistant",
                    content=f"Message {i}",
                )
                session.add(msg)
                await session.commit()
                await asyncio.sleep(0.01)  # Ensure distinct timestamps

            from sqlmodel import select
            result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.asc())
            )
            messages = list(result.scalars().all())
            assert len(messages) == 3
            assert messages[0].content == "Message 0"
            assert messages[1].content == "Message 1"
            assert messages[2].content == "Message 2"


# ---------------------------------------------------------------------------
# Tests — ChatService
# ---------------------------------------------------------------------------

class TestChatService:
    async def test_get_or_create_new_conversation(self):
        from src.services.chat_service import ChatService
        async with AsyncSessionLocal() as session:
            service = ChatService(session)
            conv = await service.get_or_create_conversation(TEST_USER)
            assert conv.id is not None
            assert conv.user_id == TEST_USER

    async def test_get_existing_conversation(self):
        from src.services.chat_service import ChatService
        async with AsyncSessionLocal() as session:
            service = ChatService(session)
            conv1 = await service.get_or_create_conversation(TEST_USER)
            conv2 = await service.get_or_create_conversation(TEST_USER, conv1.id)
            assert conv2.id == conv1.id

    async def test_get_conversation_wrong_user_raises_404(self):
        from fastapi import HTTPException
        from src.services.chat_service import ChatService
        async with AsyncSessionLocal() as session:
            service = ChatService(session)
            conv = await service.get_or_create_conversation(TEST_USER)

            with pytest.raises(HTTPException) as exc_info:
                await service.get_or_create_conversation("wrong-user", conv.id)
            assert exc_info.value.status_code == 404

    async def test_save_and_retrieve_messages(self):
        from src.services.chat_service import ChatService
        async with AsyncSessionLocal() as session:
            service = ChatService(session)
            conv = await service.get_or_create_conversation(TEST_USER)

            await service.save_message(conv.id, "user", "Hello")
            await service.save_message(conv.id, "assistant", "Hi there!")

            history = await service.get_conversation_history(conv.id)
            assert len(history) == 2
            assert history[0].role == "user"
            assert history[1].role == "assistant"

    async def test_build_input_items(self):
        from src.services.chat_service import ChatService
        messages = [
            Message(id="1", conversation_id="c", role="user", content="Hello"),
            Message(id="2", conversation_id="c", role="assistant", content="Hi!"),
        ]
        items = ChatService.build_input_items(messages)
        assert items == [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

    async def test_build_input_items_truncates(self):
        from src.services.chat_service import ChatService
        messages = [
            Message(id=str(i), conversation_id="c", role="user", content=f"Msg {i}")
            for i in range(100)
        ]
        items = ChatService.build_input_items(messages, max_messages=10)
        assert len(items) == 10
        assert items[0]["content"] == "Msg 90"
        assert items[9]["content"] == "Msg 99"
