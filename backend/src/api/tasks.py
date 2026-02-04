from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from ..database import get_sync_session
from ..models.task import TaskCreate, TaskRead, TaskUpdate
from ..models.user import User
from ..services.task_service import TaskService
from ..dependencies.auth import get_current_user
from ..errors.task_errors import TaskOwnershipError, TaskNotFoundError
from ..logging.security_logging import security_logger

# Initialize limiter for this module
limiter = Limiter(key_func=get_remote_address)


router = APIRouter(tags=["Tasks"])


@router.get("/", response_model=List[TaskRead])
@limiter.limit("30/minute")
def get_tasks(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_session)
):
    """
    Get all tasks for the current user

    This endpoint returns all tasks that belong to the currently authenticated user.
    """
    try:
        # Log data access attempt
        security_logger.log_data_access_attempt(request, str(current_user.id), "tasks", "read")

        task_service = TaskService(db)
        tasks = task_service.get_tasks_by_user(current_user.id)

        # Log successful data access
        security_logger.log_data_access_success(request, str(current_user.id), "tasks", "read")

        return tasks
    except Exception as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), "tasks", "read", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving tasks: {str(e)}"
        )


@router.post("/", response_model=TaskRead)
@limiter.limit("20/minute")
def create_task(
    request: Request,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_session)
):
    """
    Create a new task for the current user

    This endpoint creates a new task associated with the currently authenticated user.
    """
    try:
        # Log data access attempt
        security_logger.log_data_access_attempt(request, str(current_user.id), "tasks", "create")

        task_service = TaskService(db)
        task = task_service.create_task_for_user(task_data, current_user.id)

        # Log successful data access
        security_logger.log_data_access_success(request, str(current_user.id), "tasks", "create")

        return task
    except ValueError as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), "tasks", "create", str(e))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), "tasks", "create", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the task: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskRead)
@limiter.limit("30/minute")
def get_task(
    request: Request,
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_session)
):
    """
    Get a specific task by ID

    This endpoint returns a specific task if it belongs to the currently authenticated user.
    """
    try:
        # Log data access attempt
        security_logger.log_data_access_attempt(request, str(current_user.id), f"task:{task_id}", "read")

        task_service = TaskService(db)
        task = task_service.get_task_by_id_and_user(task_id, current_user.id)

        if not task:
            # Log ownership error
            security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "read", "ownership_violation")
            raise TaskOwnershipError("Task not found or does not belong to the current user")

        # Log successful data access
        security_logger.log_data_access_success(request, str(current_user.id), f"task:{task_id}", "read")

        return task
    except TaskOwnershipError:
        # Log access denied
        security_logger.log_auth_access_denied(request, str(current_user.id))

        raise
    except Exception as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "read", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the task: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskRead)
@limiter.limit("20/minute")
def update_task(
    request: Request,
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_session)
):
    """
    Update a specific task

    This endpoint updates a task if it belongs to the currently authenticated user.
    """
    try:
        # Log data access attempt
        security_logger.log_data_access_attempt(request, str(current_user.id), f"task:{task_id}", "update")

        task_service = TaskService(db)
        updated_task = task_service.update_task_by_user(
            task_id, task_data, current_user.id
        )

        # Log successful data access
        security_logger.log_data_access_success(request, str(current_user.id), f"task:{task_id}", "update")

        return updated_task
    except ValueError as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "update", str(e))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except TaskOwnershipError as e:
        # Log access denied
        security_logger.log_auth_access_denied(request, str(current_user.id))

        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "update", "ownership_violation")

        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "update", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the task: {str(e)}"
        )


@router.delete("/{task_id}")
@limiter.limit("20/minute")
def delete_task(
    request: Request,
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_session)
):
    """
    Delete a specific task

    This endpoint deletes a task if it belongs to the currently authenticated user.
    """
    try:
        # Log data access attempt
        security_logger.log_data_access_attempt(request, str(current_user.id), f"task:{task_id}", "delete")

        task_service = TaskService(db)
        task_service.delete_task_by_user(task_id, current_user.id)

        # Log successful data access
        security_logger.log_data_access_success(request, str(current_user.id), f"task:{task_id}", "delete")

        return {"message": "Task deleted successfully"}
    except TaskOwnershipError as e:
        # Log access denied
        security_logger.log_auth_access_denied(request, str(current_user.id))

        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "delete", "ownership_violation")

        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "delete", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the task: {str(e)}"
        )


@router.patch("/{task_id}/complete", response_model=TaskRead)
@limiter.limit("30/minute")
def toggle_task_completion(
    request: Request,
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_session)
):
    """
    Toggle the completion status of a task

    This endpoint toggles the is_completed status of a task if it belongs to the currently authenticated user.
    """
    try:
        # Log data access attempt
        security_logger.log_data_access_attempt(request, str(current_user.id), f"task:{task_id}", "toggle_completion")

        task_service = TaskService(db)
        updated_task = task_service.toggle_task_completion(task_id, current_user.id)

        # Log successful data access
        security_logger.log_data_access_success(request, str(current_user.id), f"task:{task_id}", "toggle_completion")

        return updated_task
    except TaskOwnershipError as e:
        # Log access denied
        security_logger.log_auth_access_denied(request, str(current_user.id))

        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "toggle_completion", "ownership_violation")

        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        # Log failed data access
        security_logger.log_data_access_failure(request, str(current_user.id), f"task:{task_id}", "toggle_completion", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while toggling task completion: {str(e)}"
        )