"""Integration tests for CLI workflows."""

from src.cli.display import format_error, format_success, format_task_details, format_task_list
from src.services.task_manager import TaskManager


def test_add_task_and_view_list_workflow() -> None:
    """Test adding a task and viewing it in the list."""
    manager = TaskManager()

    # Add a task
    task = manager.add_task("Buy groceries", "Milk, eggs, bread")

    assert task.id == 1
    assert task.title == "Buy groceries"

    # View all tasks
    tasks = manager.list_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == 1
    assert tasks[0].title == "Buy groceries"


def test_add_multiple_tasks_and_view_list() -> None:
    """Test adding multiple tasks and viewing them in correct order."""
    manager = TaskManager()

    task1 = manager.add_task("Task 1")
    task2 = manager.add_task("Task 2")
    task3 = manager.add_task("Task 3")

    tasks = manager.list_tasks()

    # Should be newest-first
    assert len(tasks) == 3
    assert tasks[0].id == task3.id
    assert tasks[1].id == task2.id
    assert tasks[2].id == task1.id


def test_add_task_toggle_complete_view_list() -> None:
    """Test adding a task, marking it complete, and viewing updated status."""
    manager = TaskManager()

    task = manager.add_task("Test Task")
    assert task.completed is False

    # Toggle complete
    manager.toggle_complete(task.id)

    # View in list
    tasks = manager.list_tasks()
    assert tasks[0].completed is True


def test_add_update_view_details() -> None:
    """Test adding a task, updating it, and viewing details."""
    manager = TaskManager()

    task = manager.add_task("Original Title", "Original Description")

    # Update task
    manager.update_task(task.id, title="Updated Title", description="Updated Description")

    # View details
    updated_task = manager.get_task(task.id)

    assert updated_task is not None
    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Updated Description"


def test_add_delete_view_list() -> None:
    """Test adding tasks, deleting one, and verifying it's removed from list."""
    manager = TaskManager()

    task1 = manager.add_task("Task 1")
    task2 = manager.add_task("Task 2")
    task3 = manager.add_task("Task 3")

    # Delete task 2
    result = manager.delete_task(task2.id)
    assert result is True

    # View list
    tasks = manager.list_tasks()
    task_ids = [t.id for t in tasks]

    assert len(tasks) == 2
    assert task2.id not in task_ids
    assert task1.id in task_ids
    assert task3.id in task_ids


def test_format_task_list_empty() -> None:
    """Test formatting an empty task list."""
    output = format_task_list([])
    assert "No tasks found" in output


def test_format_task_list_with_tasks() -> None:
    """Test formatting a task list with multiple tasks."""
    manager = TaskManager()

    manager.add_task("Task 1")
    manager.add_task("Task 2")

    tasks = manager.list_tasks()
    output = format_task_list(tasks)

    assert "All Tasks" in output
    assert "Task 1" in output
    assert "Task 2" in output
    assert "Total: 2 tasks" in output


def test_format_task_details() -> None:
    """Test formatting task details."""
    manager = TaskManager()

    task = manager.add_task("Test Task", "Test Description")
    output = format_task_details(task)

    assert "Task Details" in output
    assert "ID:" in output
    assert "Test Task" in output
    assert "Test Description" in output
    assert "Incomplete" in output


def test_format_success_message() -> None:
    """Test formatting success messages."""
    message = format_success("Task added successfully!")
    assert "[OK]" in message
    assert "Task added successfully!" in message


def test_format_error_message() -> None:
    """Test formatting error messages."""
    message = format_error("Task not found")
    assert "[ERROR]" in message
    assert "Task not found" in message


def test_complete_workflow() -> None:
    """Test a complete workflow: add, view, update, toggle, delete."""
    manager = TaskManager()

    # Add task
    task = manager.add_task("Buy groceries", "Milk, eggs, bread")
    assert task.id == 1

    # View list
    tasks = manager.list_tasks()
    assert len(tasks) == 1

    # Update task
    manager.update_task(task.id, description="Milk, eggs, bread, coffee")
    updated = manager.get_task(task.id)
    assert updated is not None
    assert "coffee" in updated.description

    # Toggle complete
    manager.toggle_complete(task.id)
    completed = manager.get_task(task.id)
    assert completed is not None
    assert completed.completed is True

    # Delete task
    result = manager.delete_task(task.id)
    assert result is True

    # Verify deleted
    tasks_after_delete = manager.list_tasks()
    assert len(tasks_after_delete) == 0
