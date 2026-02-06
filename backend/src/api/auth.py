from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request
# from src.database import get_async_session
# from src.models.user import UserCreate, UserLogin, UserRead
# from src.services.auth_service import AuthService
# from src.dependencies.auth import get_current_user
# from src.logging.security_logging import security_logger
from database import get_async_session
from models.user import UserCreate, UserLogin, UserRead
from services.auth_service import AuthService
from dependencies.auth import get_current_user
from logging.security_logging import security_logger


# Initialize limiter for this module
limiter = Limiter(key_func=get_remote_address)


router = APIRouter(tags=["Authentication"])


@router.post("/signup", response_model=UserRead)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new user account

    This endpoint registers a new user with email and password.
    The password is automatically hashed before storing.
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(user_data)

        # Log successful signup
        security_logger.log_auth_signup_success(request, str(user.id))

        return user
    except ValueError as e:
        # Log signup failure
        security_logger.log_auth_signup_failure(request, user_data.email, str(e))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log unexpected error during signup
        security_logger.log_auth_signup_failure(request, user_data.email, "unexpected_error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during registration: {str(e)}"
        )


@router.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    """
    Authenticate user and return JWT token

    This endpoint validates user credentials and returns an access token
    if authentication is successful.
    """
    try:
        # Use the AuthService for consistent authentication
        auth_service = AuthService(db)
        token_data = await auth_service.authenticate_user(
            user_credentials.email,
            user_credentials.password
        )

        if not token_data:
            # Log authentication failure
            security_logger.log_auth_login_failure(
                request,
                user_credentials.email,
                "invalid_credentials"
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Log successful authentication
        user = await auth_service.get_user_from_token(token_data["access_token"])
        if user:
            security_logger.log_auth_login_success(request, str(user.id))

        return token_data
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected error
        security_logger.log_auth_login_failure(
            request,
            user_credentials.email,
            "unexpected_error"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during login: {str(e)}"
        )


@router.post("/logout")
@limiter.limit("20/minute")
def logout(request: Request):
    """
    Logout user (client-side token invalidation)

    Note: Since JWTs are stateless, true server-side logout requires
    maintaining a blacklist of invalidated tokens, which is not implemented here.
    The client should remove the token from local storage.
    """
    # In a real implementation, you might add the token to a blacklist
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserRead)
@limiter.limit("30/minute")
def get_current_user_endpoint(
    request: Request,
    current_user: UserRead = Depends(get_current_user)
):
    """
    Get current authenticated user information

    This endpoint returns the details of the currently authenticated user.
    Requires a valid JWT token in the Authorization header.
    """
    try:
        if not current_user:
            # Log access denied
            security_logger.log_auth_access_denied(request)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return current_user
    except HTTPException:
        # Log access denied
        security_logger.log_auth_access_denied(request, getattr(current_user, 'id', None))

        raise
    except Exception as e:
        # Log unexpected error
        security_logger.log_auth_access_denied(request, getattr(current_user, 'id', None))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while retrieving user info: {str(e)}"
        )