"""Unit tests for the TaskManager service."""

import pytest

from src.services.task_manager import TaskManager


def test_add_task_success() -> None:
    """Test adding a task successfully."""
    manager = TaskManager()
    task = manager.add_task("Test Task", "Test Description")

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False


def test_add_task_with_description_only() -> None:
    """Test adding a task with only a title (no description)."""
    manager = TaskManager()
    task = manager.add_task("Test Task")

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == ""


def test_add_task_validation_empty_title() -> None:
    """Test that adding a task with empty title raises ValueError."""
    manager = TaskManager()

    with pytest.raises(ValueError, match="Title cannot be empty"):
        manager.add_task("")


def test_add_task_validation_title_too_long() -> None:
    """Test that adding a task with title > 200 chars raises ValueError."""
    manager = TaskManager()
    long_title = "a" * 201

    with pytest.raises(ValueError, match="Title must be 200 characters or less"):
        manager.add_task(long_title)


def test_add_task_validation_description_too_long() -> None:
    """Test that adding a task with description > 2000 chars raises ValueError."""
    manager = TaskManager()
    long_description = "a" * 2001

    with pytest.raises(ValueError, match="Description must be 2000 characters or less"):
        manager.add_task("Valid Title", long_description)


def test_add_task_id_assignment() -> None:
    """Test that task IDs are assigned sequentially."""
    manager = TaskManager()

    task1 = manager.add_task("Task 1")
    task2 = manager.add_task("Task 2")
    task3 = manager.add_task("Task 3")

    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3


def test_add_task_id_not_reused_after_deletion() -> None:
    """Test that deleted task IDs are not reused."""
    manager = TaskManager()

    task1 = manager.add_task("Task 1")
    manager.add_task("Task 2")

    manager.delete_task(task1.id)

    task3 = manager.add_task("Task 3")

    assert task3.id == 3  # Should be 3, not 1


def test_list_tasks_newest_first_ordering() -> None:
    """Test that list_tasks returns tasks ordered newest-first."""
    manager = TaskManager()

    task1 = manager.add_task("Task 1")
    task2 = manager.add_task("Task 2")
    task3 = manager.add_task("Task 3")

    tasks = manager.list_tasks()

    # Newest (task3) should be first
    assert tasks[0].id == task3.id
    assert tasks[1].id == task2.id
    assert tasks[2].id == task1.id


def test_list_tasks_empty() -> None:
    """Test that list_tasks returns empty list when no tasks exist."""
    manager = TaskManager()
    tasks = manager.list_tasks()

    assert tasks == []


def test_get_task_success() -> None:
    """Test retrieving a task by ID."""
    manager = TaskManager()
    task = manager.add_task("Test Task")

    retrieved = manager.get_task(task.id)

    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.title == task.title


def test_get_task_not_found() -> None:
    """Test that get_task returns None for non-existent ID."""
    manager = TaskManager()
    task = manager.get_task(999)

    assert task is None


def test_update_task_title_only() -> None:
    """Test updating only the title of a task."""
    manager = TaskManager()
    task = manager.add_task("Original Title", "Original Description")

    updated = manager.update_task(task.id, title="New Title")

    assert updated is not None
    assert updated.title == "New Title"
    assert updated.description == "Original Description"


def test_update_task_description_only() -> None:
    """Test updating only the description of a task."""
    manager = TaskManager()
    task = manager.add_task("Original Title", "Original Description")

    updated = manager.update_task(task.id, description="New Description")

    assert updated is not None
    assert updated.title == "Original Title"
    assert updated.description == "New Description"


def test_update_task_both_fields() -> None:
    """Test updating both title and description."""
    manager = TaskManager()
    task = manager.add_task("Original Title", "Original Description")

    updated = manager.update_task(task.id, title="New Title", description="New Description")

    assert updated is not None
    assert updated.title == "New Title"
    assert updated.description == "New Description"


def test_update_task_not_found() -> None:
    """Test that update_task returns None for non-existent ID."""
    manager = TaskManager()

    updated = manager.update_task(999, title="New Title")

    assert updated is None


def test_update_task_validation_error() -> None:
    """Test that update_task validates input."""
    manager = TaskManager()
    task = manager.add_task("Original Title")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        manager.update_task(task.id, title="")


def test_delete_task_success() -> None:
    """Test deleting a task successfully."""
    manager = TaskManager()
    task = manager.add_task("Test Task")

    result = manager.delete_task(task.id)

    assert result is True
    assert manager.get_task(task.id) is None


def test_delete_task_not_found() -> None:
    """Test that delete_task returns False for non-existent ID."""
    manager = TaskManager()

    result = manager.delete_task(999)

    assert result is False


def test_delete_task_removes_from_list() -> None:
    """Test that deleted task doesn't appear in list_tasks."""
    manager = TaskManager()
    task1 = manager.add_task("Task 1")
    task2 = manager.add_task("Task 2")
    task3 = manager.add_task("Task 3")

    manager.delete_task(task2.id)

    tasks = manager.list_tasks()
    task_ids = [t.id for t in tasks]

    assert task2.id not in task_ids
    assert task1.id in task_ids
    assert task3.id in task_ids


def test_toggle_complete_success() -> None:
    """Test toggling task completion status."""
    manager = TaskManager()
    task = manager.add_task("Test Task")

    assert task.completed is False

    updated = manager.toggle_complete(task.id)

    assert updated is not None
    assert updated.completed is True

    updated = manager.toggle_complete(task.id)

    assert updated is not None
    assert updated.completed is False


def test_toggle_complete_not_found() -> None:
    """Test that toggle_complete returns None for non-existent ID."""
    manager = TaskManager()

    updated = manager.toggle_complete(999)

    assert updated is None
