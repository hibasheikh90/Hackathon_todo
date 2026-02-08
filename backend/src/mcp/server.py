"""
MCP Server for Todo App — Phase 3 Part 1

Exposes 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
via the Official MCP SDK (FastMCP). Reuses the existing Phase 2 TaskService
and AsyncSessionLocal for database operations.

Transport: stdio (JSON-RPC over stdin/stdout)
Run: python -m backend.src.mcp.server
"""

import json
import logging
import sys
import os
from contextlib import asynccontextmanager
from typing import Optional

# Load environment before any database imports
from dotenv import load_dotenv

# Load .env from backend directory
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(backend_dir, ".env"))

from mcp.server.fastmcp import FastMCP

# Support both import paths:
#   - "src.*" when run from backend/ directory or in pytest
#   - "backend.src.*" when run from project root (python -m backend.src.mcp.server)
# Try src.* first to avoid duplicate model registration when conftest.py
# has already loaded models via src.* path.
try:
    from src.database import AsyncSessionLocal
    from src.models.task import TaskCreate, TaskUpdate
    from src.services.task_service import TaskService
    from src.errors.task_errors import TaskOwnershipError
except ImportError:
    from backend.src.database import AsyncSessionLocal
    from backend.src.models.task import TaskCreate, TaskUpdate
    from backend.src.services.task_service import TaskService
    from backend.src.errors.task_errors import TaskOwnershipError

# Configure logging to stderr (stdout is reserved for MCP JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("todo-mcp-server")

# Create the MCP server
mcp = FastMCP("todo-mcp-server")


# --- Session Helper (T004) ---

@asynccontextmanager
async def get_task_service():
    """Provide a TaskService with a scoped async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield TaskService(session)
        finally:
            await session.close()


# --- Tool Definitions (T005-T009) ---

@mcp.tool()
async def add_task(user_id: str, title: str, description: Optional[str] = None) -> str:
    """Create a new todo task for a user.

    Use this when the user wants to add, create, or remember something as a task.
    Returns the created task's ID, status, and title.
    """
    try:
        task_data = TaskCreate(title=title, description=description)
        async with get_task_service() as service:
            task = await service.create_task_for_user(task_data, user_id)
            return json.dumps({
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            })
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"add_task failed: {e}", exc_info=True)
        return json.dumps({"error": f"Internal error: {str(e)}"})


@mcp.tool()
async def list_tasks(user_id: str, status: Optional[str] = "all") -> str:
    """Retrieve all tasks for a user, optionally filtered by completion status.

    Use this when the user wants to see, show, or review their tasks.
    The status parameter filters results: 'all' (default), 'pending' (incomplete only),
    or 'completed' (done only). Returns an array of task objects.
    """
    # Validate status parameter
    valid_statuses = {"all", "pending", "completed"}
    if status not in valid_statuses:
        return json.dumps({"error": f"Invalid status '{status}'. Valid values: all, pending, completed"})

    try:
        async with get_task_service() as service:
            tasks = await service.get_tasks_by_user(user_id)

            # Filter by status
            if status == "pending":
                tasks = [t for t in tasks if not t.is_completed]
            elif status == "completed":
                tasks = [t for t in tasks if t.is_completed]

            return json.dumps([
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "is_completed": t.is_completed,
                    "created_at": t.created_at.isoformat(),
                }
                for t in tasks
            ])
    except Exception as e:
        logger.error(f"list_tasks failed: {e}", exc_info=True)
        return json.dumps({"error": f"Internal error: {str(e)}"})


@mcp.tool()
async def complete_task(user_id: str, task_id: str) -> str:
    """Toggle the completion status of a task.

    If the task is pending, it becomes completed. If already completed, it reverts to pending.
    Use this when the user says they finished, completed, or are done with a task.
    """
    try:
        async with get_task_service() as service:
            task = await service.toggle_task_completion(task_id, user_id)
            new_status = "completed" if task.is_completed else "pending"
            return json.dumps({
                "task_id": task.id,
                "status": new_status,
                "title": task.title,
            })
    except TaskOwnershipError:
        return json.dumps({"error": "Task not found or access denied"})
    except Exception as e:
        logger.error(f"complete_task failed: {e}", exc_info=True)
        return json.dumps({"error": f"Internal error: {str(e)}"})


@mcp.tool()
async def delete_task(user_id: str, task_id: str) -> str:
    """Permanently remove a task from the user's list.

    Use this when the user wants to delete, remove, or cancel a task.
    This action cannot be undone.
    """
    try:
        async with get_task_service() as service:
            # Pre-fetch task to capture title before deletion
            task = await service.get_task_by_id_and_user(task_id, user_id)
            if not task:
                return json.dumps({"error": "Task not found or access denied"})

            title = task.title
            await service.delete_task_by_user(task_id, user_id)
            return json.dumps({
                "task_id": task_id,
                "status": "deleted",
                "title": title,
            })
    except TaskOwnershipError:
        return json.dumps({"error": "Task not found or access denied"})
    except Exception as e:
        logger.error(f"delete_task failed: {e}", exc_info=True)
        return json.dumps({"error": f"Internal error: {str(e)}"})


@mcp.tool()
async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Modify the title and/or description of an existing task.

    Use this when the user wants to change, rename, edit, or update a task's details.
    Only the provided fields are updated; omitted fields remain unchanged.
    """
    try:
        async with get_task_service() as service:
            # Edge case: no fields to update — return current state
            if title is None and description is None:
                task = await service.get_task_by_id_and_user(task_id, user_id)
                if not task:
                    return json.dumps({"error": "Task not found or access denied"})
                return json.dumps({
                    "task_id": task.id,
                    "status": "unchanged",
                    "title": task.title,
                })

            # Build TaskUpdate with only provided fields to avoid
            # passing None values that trigger validation on unset fields
            update_fields = {}
            if title is not None:
                update_fields["title"] = title
            if description is not None:
                update_fields["description"] = description
            task_data = TaskUpdate(**update_fields)
            updated = await service.update_task_by_user(task_id, task_data, user_id)
            return json.dumps({
                "task_id": updated.id,
                "status": "updated",
                "title": updated.title,
            })
    except TaskOwnershipError:
        return json.dumps({"error": "Task not found or access denied"})
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"update_task failed: {e}", exc_info=True)
        return json.dumps({"error": f"Internal error: {str(e)}"})


# --- Entry Point ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
