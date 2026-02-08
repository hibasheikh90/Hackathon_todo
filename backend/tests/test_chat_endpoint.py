"""
Tests for the Chat API endpoint (POST /api/chat).

Tests authentication, conversation creation/continuation,
and error handling. Uses mock agent to avoid real LLM calls.
"""

import json
import os
import sys
import types
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# Module aliasing — prevent duplicate SQLAlchemy table registration.
# Do NOT add backend/src/ to sys.path — it shadows stdlib 'logging'.
# Instead, alias bare module names in sys.modules so main.py's imports work.
# ---------------------------------------------------------------------------
backend_dir = Path(__file__).parent.parent
src_dir = backend_dir / "src"

import src.models
import src.models.task
import src.models.user
import src.models.conversation
import src.models.message

if "backend" not in sys.modules:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(backend_dir)]
    sys.modules["backend"] = backend_pkg
if "backend.src" not in sys.modules:
    backend_src_pkg = types.ModuleType("backend.src")
    backend_src_pkg.__path__ = [str(src_dir)]
    sys.modules["backend.src"] = backend_src_pkg

sys.modules["backend.src.models"] = src.models
sys.modules["backend.src.models.task"] = src.models.task
sys.modules["backend.src.models.user"] = src.models.user
sys.modules["backend.src.models.conversation"] = src.models.conversation
sys.modules["backend.src.models.message"] = src.models.message

import src.database
import src.database_hf
import src.errors
import src.errors.task_errors
import src.services
import src.services.task_service
import src.services.chat_service
import src.dependencies
import src.dependencies.auth
import src.agent
import src.agent.todo_agent
import src.api
import src.api.chat
import src.api.auth
import src.api.tasks
import src.middleware
import src.middleware.input_sanitization
import src.logging
import src.logging.security_logging

# Alias bare module names so main.py's relative imports work
sys.modules["database_hf"] = src.database_hf
sys.modules["middleware"] = src.middleware
sys.modules["middleware.input_sanitization"] = src.middleware.input_sanitization
sys.modules["api"] = src.api
sys.modules["api.auth"] = src.api.auth
sys.modules["api.tasks"] = src.api.tasks
sys.modules["api.chat"] = src.api.chat

sys.modules.update({
    "backend.src.database": src.database,
    "backend.src.errors": src.errors,
    "backend.src.errors.task_errors": src.errors.task_errors,
    "backend.src.services": src.services,
    "backend.src.services.task_service": src.services.task_service,
    "backend.src.services.chat_service": src.services.chat_service,
    "backend.src.dependencies": src.dependencies,
    "backend.src.dependencies.auth": src.dependencies.auth,
    "backend.src.agent": src.agent,
    "backend.src.agent.todo_agent": src.agent.todo_agent,
    "backend.src.api": src.api,
    "backend.src.api.chat": src.api.chat,
    "backend.src.api.auth": src.api.auth,
    "backend.src.api.tasks": src.api.tasks,
    "backend.src.middleware": src.middleware,
    "backend.src.middleware.input_sanitization": src.middleware.input_sanitization,
    "backend.src.logging": src.logging,
    "backend.src.logging.security_logging": src.logging.security_logging,
})

from src.database import AsyncSessionLocal

pytestmark = pytest.mark.asyncio(loop_scope="session")

TEST_USER_ID = f"chat-test-{uuid.uuid4().hex[:8]}"
TEST_USER_EMAIL = f"{TEST_USER_ID}@test.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_run_result(final_output: str, tool_calls: list[dict] | None = None):
    """Create a mock RunResult with the given output and optional tool calls."""
    result = MagicMock()
    result.final_output = final_output
    result.new_items = []

    if tool_calls:
        from agents.items import ToolCallItem
        for tc in tool_calls:
            mock_item = MagicMock(spec=ToolCallItem)
            mock_raw = MagicMock()
            mock_raw.name = tc["tool"]
            mock_raw.arguments = json.dumps(tc.get("arguments", {}))
            mock_item.raw_item = mock_raw
            # Make isinstance check work by setting __class__
            result.new_items.append(mock_item)

    return result


def _create_jwt_token(user_id: str) -> str:
    """Create a valid JWT token for testing."""
    from jose import jwt
    import os
    from datetime import datetime, timedelta

    secret = os.getenv("BETTER_AUTH_SECRET")
    payload = {
        "sub": user_id,
        "email": TEST_USER_EMAIL,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "type": "access",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _create_expired_jwt_token(user_id: str) -> str:
    """Create an expired JWT token for testing."""
    from jose import jwt
    import os
    from datetime import datetime, timedelta

    secret = os.getenv("BETTER_AUTH_SECRET")
    payload = {
        "sub": user_id,
        "email": TEST_USER_EMAIL,
        "exp": datetime.utcnow() - timedelta(hours=1),
        "type": "access",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(autouse=True, scope="session", loop_scope="session")
async def manage_test_user():
    """Create test user at start, clean up at end."""
    from sqlalchemy import text
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
            {"id": TEST_USER_ID, "email": TEST_USER_EMAIL, "pw": "testhash"},
        )
        await session.commit()

    yield

    async with AsyncSessionLocal() as session:
        await session.execute(
            text("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :uid)"),
            {"uid": TEST_USER_ID},
        )
        await session.execute(
            text("DELETE FROM conversations WHERE user_id = :uid"),
            {"uid": TEST_USER_ID},
        )
        await session.execute(
            text("DELETE FROM users WHERE id = :uid"),
            {"uid": TEST_USER_ID},
        )
        await session.commit()


# ---------------------------------------------------------------------------
# Tests — Authentication
# ---------------------------------------------------------------------------

class TestChatAuth:
    async def test_no_auth_returns_401(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/chat", json={"message": "hello"})
            assert resp.status_code == 401

    async def test_invalid_token_returns_401(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "hello"},
                headers={"Authorization": "Bearer invalid-token"},
            )
            assert resp.status_code == 401

    async def test_expired_token_returns_401(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        token = _create_expired_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "hello"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Tests — Input Validation
# ---------------------------------------------------------------------------

class TestChatValidation:
    async def test_empty_message_returns_422(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": ""},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 422

    async def test_whitespace_only_message_returns_422(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "   "},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Tests — Chat Endpoint (with mocked agent)
# ---------------------------------------------------------------------------

class TestChatEndpoint:
    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-for-unit-tests"})
    @patch("src.api.chat.run_agent")
    @patch("src.api.chat.extract_tool_calls")
    async def test_successful_chat_new_conversation(self, mock_extract, mock_run):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        mock_run.return_value = _make_mock_run_result("Here are your tasks!")
        mock_extract.return_value = [{"tool": "list_tasks", "arguments": {"user_id": TEST_USER_ID}}]

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "Show me my tasks"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert "conversation_id" in data
        assert data["response"] == "Here are your tasks!"
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["tool"] == "list_tasks"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-for-unit-tests"})
    @patch("src.api.chat.run_agent")
    @patch("src.api.chat.extract_tool_calls")
    async def test_chat_continues_conversation(self, mock_extract, mock_run):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        mock_run.return_value = _make_mock_run_result("Task added!")
        mock_extract.return_value = []

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # First message — creates conversation
            resp1 = await client.post(
                "/api/chat",
                json={"message": "Hello"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp1.status_code == 200
            conv_id = resp1.json()["conversation_id"]

            # Second message — continues same conversation
            mock_run.return_value = _make_mock_run_result("Done!")
            resp2 = await client.post(
                "/api/chat",
                json={"message": "Add a task", "conversation_id": conv_id},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp2.status_code == 200
            assert resp2.json()["conversation_id"] == conv_id

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-for-unit-tests"})
    @patch("src.api.chat.run_agent")
    @patch("src.api.chat.extract_tool_calls")
    async def test_conversation_not_owned_returns_404(self, mock_extract, mock_run):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "hello", "conversation_id": str(uuid.uuid4())},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 404

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-for-unit-tests"})
    @patch("src.api.chat.run_agent")
    async def test_agent_timeout_returns_504(self, mock_run):
        from src.api.chat import AgentTimeoutError
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        mock_run.side_effect = AgentTimeoutError("timeout")

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "hello"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 504

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-for-unit-tests"})
    @patch("src.api.chat.run_agent")
    async def test_agent_connection_error_returns_503(self, mock_run):
        from src.api.chat import AgentConnectionError
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        mock_run.side_effect = AgentConnectionError("mcp failed")

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "hello"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 503


# ---------------------------------------------------------------------------
# Tests — Message Persistence
# ---------------------------------------------------------------------------

class TestMessagePersistence:
    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-for-unit-tests"})
    @patch("src.api.chat.run_agent")
    @patch("src.api.chat.extract_tool_calls")
    async def test_messages_persisted_in_db(self, mock_extract, mock_run):
        from httpx import AsyncClient, ASGITransport
        from src.main import app
        from sqlmodel import select
        from src.models.message import Message

        mock_run.return_value = _make_mock_run_result("Response text")
        mock_extract.return_value = []

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "Test persistence"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            conv_id = resp.json()["conversation_id"]

        # Verify messages in database
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conv_id)
                .order_by(Message.created_at.asc())
            )
            messages = list(result.scalars().all())
            assert len(messages) == 2
            assert messages[0].role == "user"
            assert messages[0].content == "Test persistence"
            assert messages[1].role == "assistant"
            assert messages[1].content == "Response text"
