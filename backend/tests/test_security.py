import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
from src.database.utils import user_crud, task_crud


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.fixture
def sync_session():
    """Create an in-memory SQLite database for testing"""
    # Use SQLite in-memory database for fast tests
    engine = create_engine("sqlite:///")

    def setup_test_db():
        with engine.begin() as conn:
            # Create all tables
            SQLModel.metadata.create_all(bind=conn)

        session = sessionmaker(engine, expire_on_commit=False)
        with session() as sess:
            yield sess

    return setup_test_db


@pytest.mark.asyncio
async def test_cross_user_task_access_prevention():
    """Test that users cannot access other users' tasks"""
    client = AsyncClient(app=app, base_url="http://testserver")

    # Create first user
    signup_data1 = {
        "email": "firstuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data1)
    assert response.status_code == 200
    user1_data = response.json()

    # Login first user
    login_data1 = {
        "email": "firstuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data1)
    assert response.status_code == 200
    token_data1 = response.json()
    access_token1 = token_data1["access_token"]

    # Create a task for the first user
    task_data = {
        "title": "First User's Task",
        "description": "This belongs to the first user",
        "is_completed": False
    }

    auth_client1 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token1}"}
    )

    response = await auth_client1.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    task1_data = response.json()
    task1_id = task1_data["id"]

    # Create second user
    client2 = AsyncClient(app=app, base_url="http://testserver")

    signup_data2 = {
        "email": "seconduser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/signup", json=signup_data2)
    assert response.status_code == 200

    # Login second user
    login_data2 = {
        "email": "seconduser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/login", json=login_data2)
    assert response.status_code == 200
    token_data2 = response.json()
    access_token2 = token_data2["access_token"]

    # Try to access the first user's task with the second user's token
    auth_client2 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token2}"}
    )

    response = await auth_client2.get(f"/api/tasks/{task1_id}")

    # Should return 404 (Not Found) or 403 (Forbidden) since user2 doesn't own task1
    assert response.status_code in [404, 403]


@pytest.mark.asyncio
async def test_cross_user_task_modification_prevention():
    """Test that users cannot modify other users' tasks"""
    client = AsyncClient(app=app, base_url="http://testserver")

    # Create first user
    signup_data1 = {
        "email": "taskowner@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data1)
    assert response.status_code == 200

    # Login first user
    login_data1 = {
        "email": "taskowner@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data1)
    assert response.status_code == 200
    token_data1 = response.json()
    access_token1 = token_data1["access_token"]

    # Create a task for the first user
    task_data = {
        "title": "Original Task",
        "description": "Original description",
        "is_completed": False
    }

    auth_client1 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token1}"}
    )

    response = await auth_client1.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    task_data_resp = response.json()
    task_id = task_data_resp["id"]

    # Create second user
    client2 = AsyncClient(app=app, base_url="http://testserver")

    signup_data2 = {
        "email": "malicioususer@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/signup", json=signup_data2)
    assert response.status_code == 200

    # Login second user
    login_data2 = {
        "email": "malicioususer@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/login", json=login_data2)
    assert response.status_code == 200
    token_data2 = response.json()
    access_token2 = token_data2["access_token"]

    # Try to update the first user's task with the second user's token
    update_data = {
        "title": "Hacked Task Title",
        "description": "Malicious user trying to update",
        "is_completed": True
    }

    auth_client2 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token2}"}
    )

    response = await auth_client2.put(f"/api/tasks/{task_id}", json=update_data)

    # Should return 404 (Not Found) or 403 (Forbidden) since user2 doesn't own the task
    assert response.status_code in [404, 403]

    # Verify the original task was not changed by getting it with the original user's token
    response = await auth_client1.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    retrieved_task = response.json()
    assert retrieved_task["title"] == "Original Task"
    assert retrieved_task["description"] == "Original description"
    assert retrieved_task["is_completed"] is False


@pytest.mark.asyncio
async def test_cross_user_task_deletion_prevention():
    """Test that users cannot delete other users' tasks"""
    client = AsyncClient(app=app, base_url="http://testserver")

    # Create first user
    signup_data1 = {
        "email": "taskowner@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data1)
    assert response.status_code == 200

    # Login first user
    login_data1 = {
        "email": "taskowner@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data1)
    assert response.status_code == 200
    token_data1 = response.json()
    access_token1 = token_data1["access_token"]

    # Create a task for the first user
    task_data = {
        "title": "Deletable Task",
        "description": "This task should not be deletable by others",
        "is_completed": False
    }

    auth_client1 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token1}"}
    )

    response = await auth_client1.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    task_data_resp = response.json()
    task_id = task_data_resp["id"]

    # Verify the task exists
    response = await auth_client1.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200

    # Create second user
    client2 = AsyncClient(app=app, base_url="http://testserver")

    signup_data2 = {
        "email": "deleteruser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/signup", json=signup_data2)
    assert response.status_code == 200

    # Login second user
    login_data2 = {
        "email": "deleteruser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/login", json=login_data2)
    assert response.status_code == 200
    token_data2 = response.json()
    access_token2 = token_data2["access_token"]

    # Try to delete the first user's task with the second user's token
    auth_client2 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token2}"}
    )

    response = await auth_client2.delete(f"/api/tasks/{task_id}")

    # Should return 404 (Not Found) or 403 (Forbidden) since user2 doesn't own the task
    assert response.status_code in [404, 403]

    # Verify the original task still exists and was not deleted
    response = await auth_client1.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    retrieved_task = response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Deletable Task"


@pytest.mark.asyncio
async def test_cross_user_task_toggle_prevention():
    """Test that users cannot toggle other users' task completion status"""
    client = AsyncClient(app=app, base_url="http://testserver")

    # Create first user
    signup_data1 = {
        "email": "taskowner@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data1)
    assert response.status_code == 200

    # Login first user
    login_data1 = {
        "email": "taskowner@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data1)
    assert response.status_code == 200
    token_data1 = response.json()
    access_token1 = token_data1["access_token"]

    # Create a task for the first user (initially not completed)
    task_data = {
        "title": "Toggle Task",
        "description": "Task for testing toggle",
        "is_completed": False
    }

    auth_client1 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token1}"}
    )

    response = await auth_client1.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    task_data_resp = response.json()
    task_id = task_data_resp["id"]

    # Verify the task is initially not completed
    response = await auth_client1.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    initial_task = response.json()
    assert initial_task["is_completed"] is False

    # Create second user
    client2 = AsyncClient(app=app, base_url="http://testserver")

    signup_data2 = {
        "email": "toggleuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/signup", json=signup_data2)
    assert response.status_code == 200

    # Login second user
    login_data2 = {
        "email": "toggleuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client2.post("/api/auth/login", json=login_data2)
    assert response.status_code == 200
    token_data2 = response.json()
    access_token2 = token_data2["access_token"]

    # Try to toggle the first user's task completion with the second user's token
    auth_client2 = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token2}"}
    )

    response = await auth_client2.patch(f"/api/tasks/{task_id}/toggle")

    # Should return 404 (Not Found) or 403 (Forbidden) since user2 doesn't own the task
    assert response.status_code in [404, 403]

    # Verify the original task's completion status was not changed
    response = await auth_client1.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    retrieved_task = response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["is_completed"] is False  # Should still be False


@pytest.mark.asyncio
async def test_user_can_access_own_tasks():
    """Test that users can access their own tasks"""
    client = AsyncClient(app=app, base_url="http://testserver")

    # Create user
    signup_data = {
        "email": "ownertester@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 200

    # Login user
    login_data = {
        "email": "ownertester@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    access_token = token_data["access_token"]

    auth_client = AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Create a task
    task_data = {
        "title": "Owner's Task",
        "description": "Task that owner should be able to access",
        "is_completed": False
    }

    response = await auth_client.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    task_resp = response.json()
    task_id = task_resp["id"]

    # User should be able to access their own task
    response = await auth_client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    retrieved_task = response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Owner's Task"

    # User should be able to update their own task
    update_data = {
        "title": "Updated Owner's Task",
        "description": "Updated description",
        "is_completed": True
    }

    response = await auth_client.put(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == "Updated Owner's Task"
    assert updated_task["is_completed"] is True

    # User should be able to delete their own task
    response = await auth_client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200

    # Task should no longer exist
    response = await auth_client.get(f"/api/tasks/{task_id}")
    assert response.status_code in [404]