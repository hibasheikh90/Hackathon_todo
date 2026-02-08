"""
Tests for the MCP Server tools.

Tests call tool handler functions directly (bypassing MCP transport)
with a real database connection to verify end-to-end behavior.

All tests in this module share a single event loop (session scope)
to avoid asyncpg connection pool issues with multiple loops.
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

import src.database
import src.database.async_utils
import src.errors
import src.errors.task_errors
import src.services
import src.services.task_service

sys.modules.update({
    "backend.src.database": src.database,
    "backend.src.database.async_utils": src.database.async_utils,
    "backend.src.errors": src.errors,
    "backend.src.errors.task_errors": src.errors.task_errors,
    "backend.src.services": src.services,
    "backend.src.services.task_service": src.services.task_service,
})

from src.database import AsyncSessionLocal
from src.mcp.server import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
)

# Use a single event loop for all tests — required because the global
# AsyncSessionLocal pool is bound to one event loop.
pytestmark = pytest.mark.asyncio(loop_scope="session")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TEST_USER_A = f"mcp-test-a-{uuid.uuid4().hex[:8]}"
TEST_USER_B = f"mcp-test-b-{uuid.uuid4().hex[:8]}"


def parse(result: str) -> dict | list:
    """Parse JSON string returned by a tool."""
    return json.loads(result)


# ---------------------------------------------------------------------------
# Fixtures — session-scoped: create users once, delete at end
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(autouse=True, scope="session", loop_scope="session")
async def manage_test_users():
    """Create test users at start, delete everything at end."""
    from sqlalchemy import text

    async with AsyncSessionLocal() as session:
        for uid in (TEST_USER_A, TEST_USER_B):
            await session.execute(
                text(
                    "INSERT INTO users (id, email, password_hash, is_active, created_at, updated_at) "
                    "VALUES (:id, :email, :pw, true, NOW(), NOW()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": uid, "email": f"{uid}@test.com", "pw": "testhash"},
            )
        await session.commit()

    yield

    async with AsyncSessionLocal() as session:
        await session.execute(
            text("DELETE FROM tasks WHERE user_id IN (:a, :b)"),
            {"a": TEST_USER_A, "b": TEST_USER_B},
        )
        await session.execute(
            text("DELETE FROM users WHERE id IN (:a, :b)"),
            {"a": TEST_USER_A, "b": TEST_USER_B},
        )
        await session.commit()


# ---------------------------------------------------------------------------
# add_task tests
# ---------------------------------------------------------------------------

class TestAddTask:
    async def test_create_task_with_title(self):
        # Retry once — the first call after pool init can hit transient DNS errors
        import asyncio
        for attempt in range(2):
            result = parse(await add_task(TEST_USER_A, "Buy groceries"))
            if "status" in result:
                break
            await asyncio.sleep(1)
        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"
        assert "task_id" in result

    async def test_create_task_with_description(self):
        result = parse(await add_task(TEST_USER_A, "Meal prep", "Chicken, rice, veggies"))
        assert result["status"] == "created"
        assert result["title"] == "Meal prep"

    async def test_create_task_empty_title_returns_error(self):
        result = parse(await add_task(TEST_USER_A, ""))
        assert "error" in result


# ---------------------------------------------------------------------------
# list_tasks tests
# ---------------------------------------------------------------------------

class TestListTasks:
    async def test_list_returns_array(self):
        result = parse(await list_tasks(TEST_USER_A))
        assert isinstance(result, list)

    async def test_list_finds_created_task(self):
        unique = f"findme-{uuid.uuid4().hex[:6]}"
        await add_task(TEST_USER_A, unique)
        result = parse(await list_tasks(TEST_USER_A))
        titles = [t["title"] for t in result]
        assert unique in titles

    async def test_list_pending_filter(self):
        tag = uuid.uuid4().hex[:6]
        await add_task(TEST_USER_A, f"pending-{tag}")
        created = parse(await add_task(TEST_USER_A, f"done-{tag}"))
        await complete_task(TEST_USER_A, created["task_id"])

        pending = parse(await list_tasks(TEST_USER_A, status="pending"))
        assert all(not t["is_completed"] for t in pending)

    async def test_list_completed_filter(self):
        created = parse(await add_task(TEST_USER_A, f"complete-{uuid.uuid4().hex[:6]}"))
        await complete_task(TEST_USER_A, created["task_id"])

        completed = parse(await list_tasks(TEST_USER_A, status="completed"))
        assert all(t["is_completed"] for t in completed)
        assert any(t["id"] == created["task_id"] for t in completed)

    async def test_list_invalid_status(self):
        result = parse(await list_tasks(TEST_USER_A, status="archived"))
        assert "error" in result

    async def test_user_isolation(self):
        tag = uuid.uuid4().hex[:6]
        a_title = f"A-only-{tag}"
        b_title = f"B-only-{tag}"
        await add_task(TEST_USER_A, a_title)
        await add_task(TEST_USER_B, b_title)

        a_tasks = parse(await list_tasks(TEST_USER_A))
        b_tasks = parse(await list_tasks(TEST_USER_B))

        a_titles = [t["title"] for t in a_tasks]
        b_titles = [t["title"] for t in b_tasks]

        assert a_title in a_titles
        assert b_title not in a_titles
        assert b_title in b_titles
        assert a_title not in b_titles


# ---------------------------------------------------------------------------
# complete_task tests
# ---------------------------------------------------------------------------

class TestCompleteTask:
    async def test_toggle_to_completed(self):
        created = parse(await add_task(TEST_USER_A, f"toggle-{uuid.uuid4().hex[:6]}"))
        result = parse(await complete_task(TEST_USER_A, created["task_id"]))
        assert result["status"] == "completed"

    async def test_toggle_back_to_pending(self):
        created = parse(await add_task(TEST_USER_A, f"toggle2-{uuid.uuid4().hex[:6]}"))
        await complete_task(TEST_USER_A, created["task_id"])
        result = parse(await complete_task(TEST_USER_A, created["task_id"]))
        assert result["status"] == "pending"

    async def test_complete_nonexistent_task(self):
        result = parse(await complete_task(TEST_USER_A, "nonexistent-id"))
        assert "error" in result

    async def test_complete_other_users_task(self):
        created = parse(await add_task(TEST_USER_A, f"private-{uuid.uuid4().hex[:6]}"))
        result = parse(await complete_task(TEST_USER_B, created["task_id"]))
        assert "error" in result


# ---------------------------------------------------------------------------
# update_task tests
# ---------------------------------------------------------------------------

class TestUpdateTask:
    async def test_update_title(self):
        created = parse(await add_task(TEST_USER_A, f"old-{uuid.uuid4().hex[:6]}"))
        result = parse(await update_task(TEST_USER_A, created["task_id"], title="New title"))
        assert result["status"] == "updated"
        assert result["title"] == "New title"

    async def test_update_description_only(self):
        created = parse(await add_task(TEST_USER_A, f"keep-{uuid.uuid4().hex[:6]}"))
        original_title = created["title"]
        result = parse(await update_task(
            TEST_USER_A, created["task_id"], description="New desc"
        ))
        assert result["status"] == "updated"
        assert result["title"] == original_title

    async def test_update_no_fields_returns_unchanged(self):
        created = parse(await add_task(TEST_USER_A, f"nochange-{uuid.uuid4().hex[:6]}"))
        result = parse(await update_task(TEST_USER_A, created["task_id"]))
        assert result["status"] == "unchanged"

    async def test_update_nonexistent_task(self):
        result = parse(await update_task(TEST_USER_A, "nonexistent-id", title="X"))
        assert "error" in result

    async def test_update_other_users_task(self):
        created = parse(await add_task(TEST_USER_A, f"priv-{uuid.uuid4().hex[:6]}"))
        result = parse(await update_task(TEST_USER_B, created["task_id"], title="Hijack"))
        assert "error" in result


# ---------------------------------------------------------------------------
# delete_task tests
# ---------------------------------------------------------------------------

class TestDeleteTask:
    async def test_delete_task(self):
        tag = uuid.uuid4().hex[:6]
        created = parse(await add_task(TEST_USER_A, f"delete-{tag}"))
        result = parse(await delete_task(TEST_USER_A, created["task_id"]))
        assert result["status"] == "deleted"
        assert f"delete-{tag}" in result["title"]

        # Verify task is gone
        tasks = parse(await list_tasks(TEST_USER_A))
        ids = [t["id"] for t in tasks]
        assert created["task_id"] not in ids

    async def test_delete_nonexistent_task(self):
        result = parse(await delete_task(TEST_USER_A, "nonexistent-id"))
        assert "error" in result

    async def test_delete_other_users_task(self):
        created = parse(await add_task(TEST_USER_A, f"priv-{uuid.uuid4().hex[:6]}"))
        result = parse(await delete_task(TEST_USER_B, created["task_id"]))
        assert "error" in result
