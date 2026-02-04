from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship
import uuid

# Use TYPE_CHECKING to avoid circular import issues
if TYPE_CHECKING:
    from .user import User


class TaskBase(SQLModel):
    """Base model for Task containing common fields"""
    title: str = Field(min_length=1, max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=10000)
    is_completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """
    Task model representing a todo item owned by a specific user

    Fields:
    - id: UUID primary key, auto-generated
    - title: Required title (1-255 characters)
    - description: Optional description (up to 10,000 characters)
    - is_completed: Boolean indicating completion status
    - created_at: Timestamp of task creation, auto-generated
    - updated_at: Timestamp of last update, auto-updated
    - user_id: UUID foreign key linking to User
    """
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Foreign key relationship to User
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)

    # Relationship to User model
    user: "User" = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    """Model for creating a new task"""
    pass


class TaskRead(TaskBase):
    """Model for reading task data"""
    id: str
    created_at: datetime
    updated_at: datetime
    user_id: str


class TaskUpdate(SQLModel):
    """Model for updating task information"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None