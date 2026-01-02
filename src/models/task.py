"""Task entity model for the todo application."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a todo item with title, description, and completion status.

    Attributes:
        id: Unique identifier for the task (auto-assigned by TaskManager)
        title: Task title (required, max 200 characters)
        description: Detailed task description (optional, max 2000 characters)
        completed: Completion status (default: False)
        created_at: Timestamp of task creation (auto-assigned)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task attributes after initialization.

        Raises:
            ValueError: If title is empty, title exceeds 200 chars,
                       or description exceeds 2000 chars
        """
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title must be 200 characters or less")
        if len(self.description) > 2000:
            raise ValueError("Description must be 2000 characters or less")

    def toggle_complete(self) -> None:
        """Toggle the completion status of the task."""
        self.completed = not self.completed

    def update(self, title: str | None = None, description: str | None = None) -> None:
        """Update task title and/or description with validation.

        Args:
            title: New title (optional, keeps current if None)
            description: New description (optional, keeps current if None)

        Raises:
            ValueError: If title is empty, title exceeds 200 chars,
                       or description exceeds 2000 chars
        """
        if title is not None:
            if not title or not title.strip():
                raise ValueError("Title cannot be empty")
            if len(title) > 200:
                raise ValueError("Title must be 200 characters or less")
            self.title = title

        if description is not None:
            if len(description) > 2000:
                raise ValueError("Description must be 2000 characters or less")
            self.description = description
