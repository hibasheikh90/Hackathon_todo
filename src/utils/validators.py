"""
Input validation functions for the Todo application.

This module provides validation functions for user inputs to ensure
data integrity and provide user-friendly error messages.
"""


def validate_title(title: str) -> None:
    """Validate task title.

    Args:
        title: The title to validate

    Raises:
        ValueError: If title is empty or exceeds 200 characters
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title) > 200:
        raise ValueError("Title must be 200 characters or less")


def validate_description(description: str) -> None:
    """Validate task description.

    Args:
        description: The description to validate

    Raises:
        ValueError: If description exceeds 1000 characters
    """
    if len(description) > 1000:
        raise ValueError("Description must be 1000 characters or less")


def validate_task_id(task_id_str: str) -> int:
    """Validate and parse task ID from user input.

    Args:
        task_id_str: The user-provided task ID string

    Returns:
        The parsed integer ID

    Raises:
        ValueError: If input is not a valid positive integer
    """
    try:
        task_id = int(task_id_str.strip())
        if task_id <= 0:
            raise ValueError("Task ID must be a positive number")
        return task_id
    except (ValueError, AttributeError):
        raise ValueError("Please enter a valid task ID number")
