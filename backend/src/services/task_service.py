import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.task import Task, TaskCreate, TaskUpdate
from ..database.async_utils import async_task_crud
from ..errors.task_errors import TaskOwnershipError, TaskNotFoundError

# Set up logging
logger = logging.getLogger(__name__)


class TaskService:
    """
    Service layer for task-related operations
    Handles business logic for task management
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tasks_by_user(self, user_id: str) -> List[Task]:
        """
        Get all tasks for a specific user

        Args:
            user_id: ID of the user whose tasks to retrieve

        Returns:
            List of tasks belonging to the user
        """
        tasks = await async_task_crud.get_tasks_by_user(self.db, user_id)
        return tasks

    async def create_task_for_user(self, task_data: TaskCreate, user_id: str) -> Task:
        """
        Create a new task for a specific user

        Args:
            task_data: TaskCreate object containing task information
            user_id: ID of the user creating the task

        Returns:
            Created Task object

        Raises:
            ValueError: If task data is invalid
        """
        # Validate task data
        if not task_data.title or task_data.title.strip() == "":
            raise ValueError("Task title cannot be empty")

        if len(task_data.title) > 255:
            raise ValueError("Task title must be 255 characters or less")

        if task_data.description and len(task_data.description) > 10000:
            raise ValueError("Task description must be 10000 characters or less")

        # Create the task
        task = await async_task_crud.create_task_for_user(self.db, task_data, user_id)
        return task

    async def get_task_by_id_and_user(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Get a specific task by its ID and user ID

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the user who owns the task

        Returns:
            Task object if found and belongs to user, None otherwise
        """
        task = await async_task_crud.get_task_by_id_and_user(self.db, task_id, user_id)

        if not task:
            logger.warning(f"Unauthorized access attempt: User {user_id} tried to access task {task_id} that does not belong to them")

        return task

    async def update_task_by_user(self, task_id: str, task_data: TaskUpdate, user_id: str) -> Optional[Task]:
        """
        Update a task if it belongs to the user

        Args:
            task_id: ID of the task to update
            task_data: TaskUpdate object with update information
            user_id: ID of the user who owns the task

        Returns:
            Updated Task object if successful, None if task doesn't belong to user
        """
        # Apply updates
        update_data = task_data.dict(exclude_unset=True)

        # Validate updates
        if "title" in update_data:
            if update_data["title"] and update_data["title"].strip() == "":
                raise ValueError("Task title cannot be empty")
            if len(update_data["title"]) > 255:
                raise ValueError("Task title must be 255 characters or less")

        if "description" in update_data and update_data["description"]:
            if len(update_data["description"]) > 10000:
                raise ValueError("Task description must be 10000 characters or less")

        # Update the task in the database
        updated_task = await async_task_crud.update_task_for_user(self.db, task_id, task_data, user_id)

        if not updated_task:
            logger.warning(f"Unauthorized access attempt: User {user_id} tried to update task {task_id} that does not belong to them")
            raise TaskOwnershipError("Task not found or does not belong to the current user")

        return updated_task

    async def delete_task_by_user(self, task_id: str, user_id: str) -> bool:
        """
        Delete a task if it belongs to the user

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user who owns the task

        Returns:
            True if deletion was successful, False if task doesn't belong to user
        """
        # Delete the task from the database
        deleted = await async_task_crud.delete_task_for_user(self.db, task_id, user_id)

        if not deleted:
            logger.warning(f"Unauthorized access attempt: User {user_id} tried to delete task {task_id} that does not belong to them")
            raise TaskOwnershipError("Task not found or does not belong to the current user")

        return deleted

    async def toggle_task_completion(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Toggle the completion status of a task

        Args:
            task_id: ID of the task to toggle
            user_id: ID of the user who owns the task

        Returns:
            Updated Task object with toggled completion status, None if task doesn't belong to user
        """
        # Get the task to toggle
        task = await self.get_task_by_id_and_user(task_id, user_id)

        if not task:
            logger.warning(f"Unauthorized access attempt: User {user_id} tried to toggle completion of task {task_id} that does not belong to them")
            raise TaskOwnershipError("Task not found or does not belong to the current user")

        # Create a TaskUpdate object with the toggled status
        task_update = TaskUpdate(is_completed=not task.is_completed)

        # Update the task in the database
        updated_task = await async_task_crud.update_task_for_user(self.db, task_id, task_update, user_id)
        return updated_task