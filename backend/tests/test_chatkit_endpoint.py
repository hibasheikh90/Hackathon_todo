"""
Tests for the ChatKit API endpoint (POST /api/chatkit).

Tests authentication, streaming responses, and agent invocation.
Uses mock agent to avoid real LLM calls.
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
import src.chatkit
import src.chatkit.store
import src.chatkit.server
import src.api
import src.api.chat
import src.api.chatkit_endpoint
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
sys.modules["api.chatkit_endpoint"] = src.api.chatkit_endpoint

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
    "backend.src.chatkit": src.chatkit,
    "backend.src.chatkit.store": src.chatkit.store,
    "backend.src.chatkit.server": src.chatkit.server,
    "backend.src.api": src.api,
    "backend.src.api.chat": src.api.chat,
    "backend.src.api.chatkit_endpoint": src.api.chatkit_endpoint,
    "backend.src.api.auth": src.api.auth,
    "backend.src.api.tasks": src.api.tasks,
    "backend.src.middleware": src.middleware,
    "backend.src.middleware.input_sanitization": src.middleware.input_sanitization,
    "backend.src.logging": src.logging,
    "backend.src.logging.security_logging": src.logging.security_logging,
})

from src.database import AsyncSessionLocal

pytestmark = pytest.mark.asyncio(loop_scope="session")

TEST_USER_ID = f"chatkit-test-{uuid.uuid4().hex[:8]}"
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
            result.new_items.append(mock_item)

    return result


def _create_jwt_token(user_id: str) -> str:
    """Create a valid JWT token for testing."""
    from jose import jwt
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

class TestChatKitAuth:
    async def test_no_auth_returns_401(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/chatkit", content=b"{}")
            assert resp.status_code == 401

    async def test_invalid_token_returns_401(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chatkit",
                content=b"{}",
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
                "/api/chatkit",
                content=b"{}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Tests — API Key Validation
# ---------------------------------------------------------------------------

class TestChatKitAPIKey:
    async def test_missing_api_key_returns_503(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
                resp = await client.post(
                    "/api/chatkit",
                    content=b"{}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert resp.status_code == 503

    async def test_placeholder_api_key_returns_503(self):
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        token = _create_jwt_token(TEST_USER_ID)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-your-key-here"}, clear=False):
                resp = await client.post(
                    "/api/chatkit",
                    content=b"{}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert resp.status_code == 503


# ---------------------------------------------------------------------------
# Tests — Server Passes User ID
# ---------------------------------------------------------------------------

class TestChatKitUserIdInjection:
    async def test_server_passes_user_id_to_agent(self):
        """Verify that the ChatKit server extracts user_id from JWT context."""
        from src.chatkit.server import TodoChatKitServer, create_chatkit_server
        from chatkit.types import (
            ThreadMetadata, UserMessageItem, UserMessageTextContent,
            InferenceOptions, Page,
        )
        from datetime import datetime, timezone

        server = create_chatkit_server()

        thread = ThreadMetadata(
            id="test-thread-1",
            created_at=datetime.now(timezone.utc),
        )

        user_msg = UserMessageItem(
            id="msg-1",
            thread_id="test-thread-1",
            created_at=datetime.now(timezone.utc),
            content=[UserMessageTextContent(text="Show me my tasks")],
            inference_options=InferenceOptions(),
        )

        mock_result = _make_mock_run_result(
            "Here are your tasks...",
            tool_calls=[{"tool": "list_tasks", "arguments": {"user_id": TEST_USER_ID}}],
        )

        with patch("src.chatkit.server.run_agent", new_callable=AsyncMock, return_value=mock_result) as mock_agent:
            with patch.object(server.store, "load_thread_items", new_callable=AsyncMock) as mock_items:
                mock_items.return_value = Page(
                    data=[user_msg],
                    has_more=False,
                    after=None,
                )

                events = []
                async for event in server.respond(
                    thread, user_msg, context={"user_id": TEST_USER_ID}
                ):
                    events.append(event)

                # Verify agent was called with correct user_id
                mock_agent.assert_called_once()
                call_kwargs = mock_agent.call_args
                assert call_kwargs.kwargs.get("user_id") == TEST_USER_ID

                # Verify we got a response event
                assert len(events) >= 1
