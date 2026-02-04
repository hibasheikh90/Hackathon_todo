from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os
from typing import Optional
from ..database import get_sync_session
from ..models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_sync_session)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    This function:
    1. Extracts and validates the JWT token from the Authorization header
    2. Verifies the token signature and expiration
    3. Extracts the user ID from the token payload
    4. Retrieves the user from the database
    5. Returns the user object or raises an HTTP exception if invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Get secret key from environment
        secret_key = os.getenv("BETTER_AUTH_SECRET")
        if not secret_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing authentication secret"
            )

        # Decode the token
        payload = jwt.decode(
            credentials.credentials,
            secret_key,
            algorithms=["HS256"],
            options={"verify_exp": True}  # Verify expiration
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Query the database for the user using sync session
    from sqlmodel import select
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Convenience dependency that ensures the user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return current_user


def get_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract only the user ID from the token without querying the database
    Useful for lightweight operations that only need the identity
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        secret_key = os.getenv("BETTER_AUTH_SECRET")
        if not secret_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing authentication secret"
            )

        payload = jwt.decode(
            credentials.credentials,
            secret_key,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return user_id

    except JWTError:
        raise credentials_exception


# Optional: Role-based access control dependencies
def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that requires the user to have admin privileges
    """
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Simple dependency that just requires authentication
    """
    return current_user