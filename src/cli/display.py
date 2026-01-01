"""
Display and output formatting functions for the CLI.

This module handles all visual output including task tables, headers,
and styled messages (success, error, info).
"""

from typing import List
from ..core.models import Task
from ..utils.formatters import truncate_text


def display_header(text: str) -> None:
    """Display a formatted section header.

    Args:
        text: The header text to display
    """
    print(f"\n{'=' * 50}")
    print(f"  {text}")
    print(f"{'=' * 50}\n")


def display_tasks(tasks: List[Task]) -> None:
    """Display a formatted list of tasks in a table.

    Args:
        tasks: List of Task objects to display
    """
    if not tasks:
        print("No tasks yet. Add one to get started!\n")
        return

    print(f"\n{'-' * 70}")
    print(f"{'ID':<5} {'Status':<8} {'Title':<40} {'Description':<15}")
    print(f"{'-' * 70}")

    for task in tasks:
        status_icon = "[X]" if task.completed else "[ ]"
        title_truncated = truncate_text(task.title, 40)
        desc_truncated = truncate_text(task.description, 15)

        print(f"{task.id:<5} {status_icon:<8} {title_truncated:<40} {desc_truncated:<15}")

    print(f"{'-' * 70}\n")


def show_success(message: str) -> None:
    """Display a success message.

    Args:
        message: The success message to display
    """
    print(f"\n[SUCCESS] {message}\n")


def show_error(message: str) -> None:
    """Display an error message.

    Args:
        message: The error message to display
    """
    print(f"\n[ERROR] {message}\n")


def show_info(message: str) -> None:
    """Display an informational message.

    Args:
        message: The info message to display
    """
    print(f"\n[INFO] {message}\n")
