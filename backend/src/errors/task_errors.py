from fastapi import HTTPException, status


class TaskOwnershipError(HTTPException):
    """
    Exception raised when a user tries to access a task they don't own
    """
    def __init__(self, detail: str = "Task does not belong to the current user"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class TaskNotFoundError(HTTPException):
    """
    Exception raised when a task is not found
    """
    def __init__(self, detail: str = "Task not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class TaskValidationError(HTTPException):
    """
    Exception raised when task data is invalid
    """
    def __init__(self, detail: str = "Invalid task data"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class UnauthorizedAccessError(HTTPException):
    """
    Exception raised when a user tries to perform an unauthorized action
    """
    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


# Helper functions for common error responses
def raise_ownership_error():
    """Raise a TaskOwnershipError with a standard message"""
    raise TaskOwnershipError()


def raise_task_not_found():
    """Raise a TaskNotFoundError with a standard message"""
    raise TaskNotFoundError()


def raise_task_validation_error(detail: str = "Invalid task data"):
    """Raise a TaskValidationError with a custom message"""
    raise TaskValidationError(detail)