"""
TaskManager - Business logic for task CRUD operations.

This module manages all task operations including creation, retrieval,
updates, deletion, and status toggling. Tasks are stored in-memory
using a dictionary.
"""

from typing import Dict, List, Optional
from .models import Task
from ..utils.validators import validate_title, validate_description


class TaskManager:
    """Manages all task CRUD operations and in-memory storage.

    Storage: Dictionary mapping task IDs to Task objects.
    ID Strategy: Auto-incrementing integer starting from 1.
    """

    def __init__(self):
        """Initialize the TaskManager with empty storage."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Create a new task.

        Args:
            title: Task title (will be validated)
            description: Optional task description (will be validated)

        Returns:
            The newly created Task object

        Raises:
            ValueError: If title or description validation fails
        """
        validate_title(title)
        validate_description(description)

        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description.strip()
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks.

        Returns:
            List of all Task objects, ordered by ID (creation order)
        """
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a single task by ID.

        Args:
            task_id: The task's unique identifier

        Returns:
            Task object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Task:
        """Update a task's title and/or description.

        Args:
            task_id: The task's unique identifier
            title: New title (None to keep existing)
            description: New description (None to keep existing)

        Returns:
            The updated Task object

        Raises:
            ValueError: If task_id doesn't exist or validation fails
        """
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found")

        if title is None and description is None:
            raise ValueError("At least one field (title or description) must be provided")

        # Validate and update new values
        if title is not None:
            validate_title(title)
            task.title = title.strip()

        if description is not None:
            validate_description(description)
            task.description = description.strip()

        return task

    def delete_task(self, task_id: int) -> Task:
        """Delete a task by ID.

        Args:
            task_id: The task's unique identifier

        Returns:
            The deleted Task object (for confirmation message)

        Raises:
            ValueError: If task_id doesn't exist
        """
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found")

        del self._tasks[task_id]
        return task

    def toggle_status(self, task_id: int) -> Task:
        """Toggle a task's completion status.

        Args:
            task_id: The task's unique identifier

        Returns:
            The updated Task object

        Raises:
            ValueError: If task_id doesn't exist
        """
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found")

        task.completed = not task.completed
        return task
