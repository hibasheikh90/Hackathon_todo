import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from uuid import uuid4
import sys
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from .test_app import app  # Test app for testing
from src.models.user import UserCreate, User
from src.models.task import TaskCreate, Task
from src.services.auth_service import AuthService


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.fixture
async def async_session():
    """Create an in-memory SQLite database for testing"""
    # Use SQLite in-memory database for fast tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async def setup_test_db():
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)

        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session

    return setup_test_db


@pytest.fixture
async def authenticated_client(client):
    """Create a client with an authenticated user"""
    # Create a test user
    signup_data = {
        "email": "taskuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 200

    # Login to get a token
    login_data = {
        "email": "taskuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    access_token = token_data["access_token"]

    # Create a new client with the token
    auth_client = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    return auth_client


@pytest.mark.asyncio
async def test_create_task_success(authenticated_client):
    """Test creating a new task successfully"""
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)

    assert response.status_code == 200

    task_response = response.json()
    assert "id" in task_response
    assert task_response["title"] == "Test Task"
    assert task_response["description"] == "This is a test task"
    assert task_response["is_completed"] is False
    assert "user_id" in task_response


@pytest.mark.asyncio
async def test_create_task_missing_title(authenticated_client):
    """Test creating a task without a title"""
    task_data = {
        "description": "This is a test task",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_task_empty_title(authenticated_client):
    """Test creating a task with an empty title"""
    task_data = {
        "title": "",
        "description": "This is a test task",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_task_long_title(authenticated_client):
    """Test creating a task with a title that's too long"""
    task_data = {
        "title": "x" * 256,  # Exceeds max length of 255
        "description": "This is a test task",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_tasks_list(authenticated_client):
    """Test getting a list of tasks for the authenticated user"""
    # First, create a task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)
    assert response.status_code == 200

    # Now get the list of tasks
    response = await authenticated_client.get("/api/tasks")

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) >= 1

    # Check that our task is in the list
    found_task = next((t for t in tasks if t["title"] == "Test Task"), None)
    assert found_task is not None


@pytest.mark.asyncio
async def test_get_specific_task(authenticated_client):
    """Test getting a specific task by ID"""
    # Create a task
    task_data = {
        "title": "Specific Task",
        "description": "This is a specific task",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)
    assert response.status_code == 200

    created_task = response.json()
    task_id = created_task["id"]

    # Get the specific task
    response = await authenticated_client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200

    retrieved_task = response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Specific Task"


@pytest.mark.asyncio
async def test_update_task(authenticated_client):
    """Test updating a task"""
    # Create a task
    task_data = {
        "title": "Original Task",
        "description": "Original description",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)
    assert response.status_code == 200

    created_task = response.json()
    task_id = created_task["id"]

    # Update the task
    update_data = {
        "title": "Updated Task",
        "description": "Updated description",
        "is_completed": True
    }

    response = await authenticated_client.put(f"/api/tasks/{task_id}", json=update_data)

    assert response.status_code == 200

    updated_task = response.json()
    assert updated_task["id"] == task_id
    assert updated_task["title"] == "Updated Task"
    assert updated_task["description"] == "Updated description"
    assert updated_task["is_completed"] is True


@pytest.mark.asyncio
async def test_delete_task(authenticated_client):
    """Test deleting a task"""
    # Create a task
    task_data = {
        "title": "Task to Delete",
        "description": "This task will be deleted",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)
    assert response.status_code == 200

    created_task = response.json()
    task_id = created_task["id"]

    # Delete the task
    response = await authenticated_client.delete(f"/api/tasks/{task_id}")

    assert response.status_code == 200

    # Verify the task is gone by trying to get it
    response = await authenticated_client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_task_completion(authenticated_client):
    """Test toggling a task's completion status"""
    # Create a task
    task_data = {
        "title": "Toggle Task",
        "description": "This task will be toggled",
        "is_completed": False
    }

    response = await authenticated_client.post("/api/tasks", json=task_data)
    assert response.status_code == 200

    created_task = response.json()
    task_id = created_task["id"]

    # Verify initial state
    assert created_task["is_completed"] is False

    # Toggle the task completion
    response = await authenticated_client.patch(f"/api/tasks/{task_id}/toggle")

    assert response.status_code == 200

    toggled_task = response.json()
    assert toggled_task["id"] == task_id
    assert toggled_task["is_completed"] is True  # Should now be completed

    # Toggle again to make sure it goes back to incomplete
    response = await authenticated_client.patch(f"/api/tasks/{task_id}/toggle")

    assert response.status_code == 200

    toggled_again_task = response.json()
    assert toggled_again_task["id"] == task_id
    assert toggled_again_task["is_completed"] is False  # Should now be incomplete


@pytest.mark.asyncio
async def test_cross_user_task_isolation(authenticated_client):
    """Test that users can't access other users' tasks"""
    # Create a second user and get their token
    client2 = AsyncClient(app=app, base_url="http://testserver")

    # Create second user
    signup_data = {
        "email": "seconduser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 200

    # Login second user
    login_data = {
        "email": "seconduser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    access_token2 = token_data["access_token"]

    # Create a task for the second user
    task_data = {
        "title": "Second User's Task",
        "description": "This belongs to the second user",
        "is_completed": False
    }

    auth_client2 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token2}"}
    )

    response = await auth_client2.post("/api/tasks", json=task_data)
    assert response.status_code == 200

    second_user_task = response.json()
    second_user_task_id = second_user_task["id"]

    # Try to access the second user's task with the first user's token
    # This should fail or return nothing
    response = await authenticated_client.get(f"/api/tasks/{second_user_task_id}")

    # Depending on implementation, this might return 404 or 403
    # The important thing is that the first user can't access the second user's task
    assert response.status_code in [404, 403]


@pytest.mark.asyncio
async def test_unauthorized_access_to_tasks():
    """Test that unauthenticated users can't access tasks endpoints"""
    client = AsyncClient(app=app, base_url="http://testserver")

    # Try to create a task without authentication
    task_data = {
        "title": "Unauthorized Task",
        "description": "This should fail",
        "is_completed": False
    }

    response = await client.post("/api/tasks", json=task_data)

    assert response.status_code == 401

    # Try to get tasks without authentication
    response = await client.get("/api/tasks")

    assert response.status_code == 401