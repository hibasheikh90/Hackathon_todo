"""
Task data model for the Todo application.

This module defines the Task dataclass representing a single todo item
with all its attributes and behaviors.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a single todo task.

    Attributes:
        id: Unique identifier (auto-assigned by TaskManager)
        title: Task title (1-200 chars)
        description: Optional detailed description (0-1000 chars)
        completed: Completion status (default: False)
        created_at: Timestamp of creation (ISO 8601 string)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __str__(self) -> str:
        """Return human-readable representation of the task.

        Returns:
            Formatted string with status icon, ID, and title
        """
        status = "X" if self.completed else " "
        return f"[{status}] (ID: {self.id}) {self.title}"
