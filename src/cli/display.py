"""Display and output formatting functions for the CLI."""

from src.models.task import Task


def format_success(message: str) -> str:
    """Format a success message with checkmark symbol.

    Args:
        message: The success message to format

    Returns:
        Formatted success message with [OK] prefix
    """
    return f"[OK] {message}"


def format_error(message: str) -> str:
    """Format an error message with X symbol.

    Args:
        message: The error message to format

    Returns:
        Formatted error message with [ERROR] prefix
    """
    return f"[ERROR] {message}"


def format_task_list(tasks: list[Task]) -> str:
    """Format a list of tasks in tabular format.

    Displays ID, Status ([x] or [ ]), and Title columns.
    Tasks should be ordered newest-first.

    Args:
        tasks: List of Task objects to display

    Returns:
        Formatted task list as a string
    """
    if not tasks:
        return "=== All Tasks ===\nNo tasks found. Add your first task to get started!"

    output = "=== All Tasks ===\n"
    output += "ID  Status  Title\n"
    output += "--  ------  -----\n"

    for task in tasks:
        status = "[x]" if task.completed else "[ ]"
        output += f"{task.id:<4}{status:<8}{task.title}\n"

    task_count = len(tasks)
    task_word = "task" if task_count == 1 else "tasks"
    output += f"\nTotal: {task_count} {task_word}"

    return output


def format_task_details(task: Task) -> str:
    """Format full task details including description.

    Args:
        task: The Task object to display

    Returns:
        Formatted task details as a string
    """
    status = "Completed" if task.completed else "Incomplete"
    created = task.created_at.strftime("%Y-%m-%d %H:%M:%S")

    output = "=== Task Details ===\n"
    output += f"ID: {task.id}\n"
    output += f"Title: {task.title}\n"
    output += f"Description: {task.description if task.description else '(none)'}\n"
    output += f"Status: {status}\n"
    output += f"Created: {created}"

    return output
