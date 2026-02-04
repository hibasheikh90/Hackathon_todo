import pytest
import uuid
from datetime import datetime
from sqlmodel import SQLModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import User, UserCreate, UserRead, UserUpdate, UserLogin
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate


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


def test_user_model_creation():
    """Test creating a User model instance"""
    user_data = {
        "email": "test@example.com",
        "password_hash": "hashed_password_here",
    }

    user = User(**user_data)

    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_password_here"
    assert isinstance(user.id, uuid.UUID)
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)
    assert user.is_active is True  # Default value


def test_user_create_model():
    """Test UserCreate model validation"""
    user_create_data = {
        "email": "newuser@example.com",
        "password": "securepassword123"
    }

    user_create = UserCreate(**user_create_data)

    assert user_create.email == "newuser@example.com"
    assert user_create.password == "securepassword123"


def test_user_read_model():
    """Test UserRead model serialization"""
    user_id = uuid.uuid4()
    created_time = datetime.utcnow()

    user_read = UserRead(
        id=user_id,
        email="readonly@example.com",
        is_active=True,
        created_at=created_time,
        updated_at=created_time
    )

    assert user_read.id == user_id
    assert user_read.email == "readonly@example.com"
    assert user_read.is_active is True
    assert user_read.created_at == created_time
    assert user_read.updated_at == created_time


def test_user_update_model():
    """Test UserUpdate model partial updates"""
    user_update_data = {
        "email": "updated@example.com",
        "is_active": False
    }

    user_update = UserUpdate(**user_update_data)

    assert user_update.email == "updated@example.com"
    assert user_update.is_active is False


def test_user_login_model():
    """Test UserLogin model for authentication"""
    login_data = {
        "email": "login@example.com",
        "password": "userpassword"
    }

    user_login = UserLogin(**login_data)

    assert user_login.email == "login@example.com"
    assert user_login.password == "userpassword"


def test_task_model_creation():
    """Test creating a Task model instance"""
    user_id = uuid.uuid4()
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "is_completed": False,
        "user_id": user_id
    }

    task = Task(**task_data)

    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.is_completed is False
    assert task.user_id == user_id
    assert isinstance(task.id, uuid.UUID)
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_create_model():
    """Test TaskCreate model validation"""
    task_create_data = {
        "title": "New Task",
        "description": "Description for new task",
        "is_completed": False
    }

    task_create = TaskCreate(**task_create_data)

    assert task_create.title == "New Task"
    assert task_create.description == "Description for new task"
    assert task_create.is_completed is False


def test_task_read_model():
    """Test TaskRead model serialization"""
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    created_time = datetime.utcnow()

    task_read = TaskRead(
        id=task_id,
        title="Read Task",
        description="Task for reading",
        is_completed=True,
        created_at=created_time,
        updated_at=created_time,
        user_id=user_id
    )

    assert task_read.id == task_id
    assert task_read.title == "Read Task"
    assert task_read.description == "Task for reading"
    assert task_read.is_completed is True
    assert task_read.user_id == user_id
    assert task_read.created_at == created_time
    assert task_read.updated_at == created_time


def test_task_update_model():
    """Test TaskUpdate model partial updates"""
    task_update_data = {
        "title": "Updated Task Title",
        "is_completed": True
    }

    task_update = TaskUpdate(**task_update_data)

    assert task_update.title == "Updated Task Title"
    assert task_update.is_completed is True
    # Description should be None since it wasn't provided
    assert task_update.description is None


def test_task_title_validation():
    """Test that Task title validation works"""
    # Test minimum length (should fail if empty)
    with pytest.raises(ValueError):
        Task(title="", description="Valid description", user_id=uuid.uuid4())

    # Test maximum length (should succeed with 255 chars)
    long_title = "a" * 255
    task = Task(title=long_title, description="Valid description", user_id=uuid.uuid4())
    assert task.title == long_title


def test_task_description_length():
    """Test Task description length limits"""
    # Create a task with a very long description (under limit)
    long_description = "x" * 9999  # Under the 10,000 char limit
    user_id = uuid.uuid4()

    task = Task(
        title="Long Description Task",
        description=long_description,
        user_id=user_id
    )

    assert task.description == long_description
    assert len(task.description) == 9999


def test_user_task_relationship():
    """Test the relationship between User and Task models"""
    # Note: In this test, we're just checking the model structure
    # The actual relationship is tested in integration tests
    user_id = uuid.uuid4()

    user = User(
        email="relationship@example.com",
        password_hash="hash",
        id=user_id
    )

    task = Task(
        title="Related Task",
        user_id=user_id
    )

    assert task.user_id == user.id


def test_task_default_values():
    """Test default values for Task model"""
    user_id = uuid.uuid4()

    # Create task without specifying optional fields
    task = Task(title="Default Values Task", user_id=user_id)

    # Check default values
    assert task.is_completed is False
    assert task.description is None
    assert isinstance(task.id, uuid.UUID)
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)
    assert task.user_id == user_id


def test_user_default_values():
    """Test default values for User model"""
    # Create user without specifying optional fields
    user = User(
        email="defaults@example.com",
        password_hash="hash"
    )

    # Check default values
    assert user.is_active is True
    assert isinstance(user.id, uuid.UUID)
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


# Test the database models with actual database session
def test_user_database_operations(sync_session):
    """Test creating and retrieving User from database"""
    for session in sync_session():
        # Create a user
        user = User(
            email="db@example.com",
            password_hash="hashed_password"
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Retrieve the user
        from sqlmodel import select
        result = session.exec(select(User).where(User.email == "db@example.com"))
        retrieved_user = result.first()

        assert retrieved_user is not None
        assert retrieved_user.email == "db@example.com"
        assert retrieved_user.password_hash == "hashed_password"
        assert retrieved_user.id == user.id


def test_task_database_operations(sync_session):
    """Test creating and retrieving Task from database"""
    for session in sync_session():
        # Create a user first
        user = User(
            email="taskowner@example.com",
            password_hash="hashed_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create a task for the user
        task = Task(
            title="Database Task",
            description="Task created in database",
            user_id=user.id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Retrieve the task
        from sqlmodel import select
        result = session.exec(select(Task).where(Task.id == task.id))
        retrieved_task = result.first()

        assert retrieved_task is not None
        assert retrieved_task.title == "Database Task"
        assert retrieved_task.description == "Task created in database"
        assert retrieved_task.user_id == user.id
        assert retrieved_task.id == task.id