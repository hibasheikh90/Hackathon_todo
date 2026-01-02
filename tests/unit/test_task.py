"""Unit tests for the Task model."""

from datetime import datetime

import pytest

from src.models.task import Task


def test_task_creation_with_all_fields() -> None:
    """Test creating a task with all fields specified."""
    created_time = datetime.now()
    task = Task(
        id=1,
        title="Test Task",
        description="Test Description",
        completed=False,
        created_at=created_time,
    )

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert task.created_at == created_time


def test_task_creation_with_defaults() -> None:
    """Test creating a task with default values."""
    task = Task(id=1, title="Test Task")

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == ""
    assert task.completed is False
    assert isinstance(task.created_at, datetime)


def test_task_validation_empty_title() -> None:
    """Test that creating a task with empty title raises ValueError."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Task(id=1, title="")


def test_task_validation_whitespace_title() -> None:
    """Test that creating a task with whitespace-only title raises ValueError."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Task(id=1, title="   ")


def test_task_validation_title_too_long() -> None:
    """Test that creating a task with title > 200 chars raises ValueError."""
    long_title = "a" * 201
    with pytest.raises(ValueError, match="Title must be 200 characters or less"):
        Task(id=1, title=long_title)


def test_task_validation_title_exactly_200_chars() -> None:
    """Test that creating a task with exactly 200 char title succeeds."""
    title_200 = "a" * 200
    task = Task(id=1, title=title_200)
    assert len(task.title) == 200


def test_task_validation_description_too_long() -> None:
    """Test that creating a task with description > 2000 chars raises ValueError."""
    long_description = "a" * 2001
    with pytest.raises(ValueError, match="Description must be 2000 characters or less"):
        Task(id=1, title="Valid Title", description=long_description)


def test_task_validation_description_exactly_2000_chars() -> None:
    """Test that creating a task with exactly 2000 char description succeeds."""
    description_2000 = "a" * 2000
    task = Task(id=1, title="Valid Title", description=description_2000)
    assert len(task.description) == 2000


def test_toggle_complete_from_incomplete() -> None:
    """Test toggling task from incomplete to complete."""
    task = Task(id=1, title="Test Task", completed=False)
    task.toggle_complete()
    assert task.completed is True


def test_toggle_complete_from_complete() -> None:
    """Test toggling task from complete to incomplete."""
    task = Task(id=1, title="Test Task", completed=True)
    task.toggle_complete()
    assert task.completed is False


def test_toggle_complete_multiple_times() -> None:
    """Test toggling task multiple times."""
    task = Task(id=1, title="Test Task", completed=False)

    task.toggle_complete()
    assert task.completed is True

    task.toggle_complete()
    assert task.completed is False

    task.toggle_complete()
    assert task.completed is True


def test_update_title_only() -> None:
    """Test updating only the title."""
    task = Task(id=1, title="Original Title", description="Original Description")
    task.update(title="New Title")

    assert task.title == "New Title"
    assert task.description == "Original Description"


def test_update_description_only() -> None:
    """Test updating only the description."""
    task = Task(id=1, title="Original Title", description="Original Description")
    task.update(description="New Description")

    assert task.title == "Original Title"
    assert task.description == "New Description"


def test_update_both_title_and_description() -> None:
    """Test updating both title and description."""
    task = Task(id=1, title="Original Title", description="Original Description")
    task.update(title="New Title", description="New Description")

    assert task.title == "New Title"
    assert task.description == "New Description"


def test_update_with_empty_title() -> None:
    """Test that updating with empty title raises ValueError."""
    task = Task(id=1, title="Original Title")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        task.update(title="")


def test_update_with_whitespace_title() -> None:
    """Test that updating with whitespace-only title raises ValueError."""
    task = Task(id=1, title="Original Title")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        task.update(title="   ")


def test_update_with_title_too_long() -> None:
    """Test that updating with title > 200 chars raises ValueError."""
    task = Task(id=1, title="Original Title")
    long_title = "a" * 201

    with pytest.raises(ValueError, match="Title must be 200 characters or less"):
        task.update(title=long_title)


def test_update_with_description_too_long() -> None:
    """Test that updating with description > 2000 chars raises ValueError."""
    task = Task(id=1, title="Original Title")
    long_description = "a" * 2001

    with pytest.raises(ValueError, match="Description must be 2000 characters or less"):
        task.update(description=long_description)


def test_update_preserves_original_on_validation_error() -> None:
    """Test that failed update preserves original values."""
    task = Task(id=1, title="Original Title", description="Original Description")

    with pytest.raises(ValueError):
        task.update(title="")

    # Original values should be preserved
    assert task.title == "Original Title"
    assert task.description == "Original Description"
