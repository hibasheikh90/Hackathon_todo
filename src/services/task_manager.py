"""Task management service with CRUD operations."""

from src.models.task import Task


class TaskManager:
    """Manages in-memory storage and CRUD operations for tasks.

    Uses a dictionary for O(1) lookup by task ID. Tasks are stored in memory
    and will be lost when the application exits.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects
        _next_id: Counter for generating unique task IDs
    """

    def __init__(self) -> None:
        """Initialize the task manager with empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Create and store a new task.

        Args:
            title: Task title (required)
            description: Task description (optional, default: "")

        Returns:
            The newly created Task object

        Raises:
            ValueError: If validation fails (empty title, max lengths exceeded)
        """
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task | None:
        """Retrieve a task by ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            Task object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        """Retrieve all tasks, sorted newest-first by creation time.

        Returns:
            List of Task objects, sorted by created_at descending
        """
        return sorted(self._tasks.values(), key=lambda task: task.created_at, reverse=True)

    def update_task(
        self, task_id: int, title: str | None = None, description: str | None = None
    ) -> Task | None:
        """Update a task's title and/or description.

        Args:
            task_id: The unique identifier of the task
            title: New title (optional, keeps current if None)
            description: New description (optional, keeps current if None)

        Returns:
            Updated Task object if found, None otherwise

        Raises:
            ValueError: If validation fails (empty title, max lengths exceeded)
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        task.update(title=title, description=description)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            True if task was deleted, False if task not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> Task | None:
        """Toggle the completion status of a task.

        Args:
            task_id: The unique identifier of the task

        Returns:
            Updated Task object if found, None otherwise
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        task.toggle_complete()
        return task
