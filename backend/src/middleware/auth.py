from fastapi import Request, HTTPException, status
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
import os
from backend.src.models.user import UserRead


class JWTBearer(HTTPBearer):
    """
    JWT Bearer authentication middleware for FastAPI
    Validates JWT tokens and extracts user information
    """

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        # Get credentials from Authorization header
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme."
                )
            token = credentials.credentials
            user_id = self.verify_jwt(token)

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or expired token."
                )

            # Store user_id in request state for use in endpoints
            request.state.user_id = user_id
            return token
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code."
            )

    def verify_jwt(self, jwtoken: str) -> Optional[str]:
        """
        Verify JWT token and return user ID if valid
        """
        try:
            # Get secret from environment variable
            secret_key = os.getenv("BETTER_AUTH_SECRET")
            if not secret_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing authentication secret"
                )

            # Decode the token
            payload = jwt.decode(
                jwtoken,
                secret_key,
                algorithms=["HS256"],
                options={"verify_exp": True}  # Verify expiration
            )

            # Extract user_id from payload
            user_id = payload.get("sub")
            if user_id:
                return user_id

            return None

        except JWTError:
            return None


# Alternative middleware approach for more complex scenarios
class AuthMiddleware:
    """
    Alternative authentication middleware class
    Can be used with Starlette middleware if needed
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)

        # Extract token from headers
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]

            # Verify token and extract user info
            user_id = self.verify_token(token)
            if user_id:
                request.state.user_id = user_id

        return await self.app(scope, receive, send)

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user ID"""
        try:
            secret_key = os.getenv("BETTER_AUTH_SECRET")
            if not secret_key:
                return None

            payload = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"],
                options={"verify_exp": True}
            )

            return payload.get("sub")
        except JWTError:
            return None


# Utility function to get current user from token
def get_current_user_from_token(token: str) -> Optional[UserRead]:
    """
    Extract user information from JWT token
    Useful for dependency injection
    """
    try:
        secret_key = os.getenv("BETTER_AUTH_SECRET")
        if not secret_key:
            return None

        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"]
        )

        user_id = payload.get("sub")
        email = payload.get("email")

        if user_id and email:
            # Create a UserRead object from the token data
            from datetime import datetime
            return UserRead(
                id=user_id,
                email=email,
                is_active=payload.get("is_active", True),
                created_at=datetime.fromisoformat(payload.get("created_at", datetime.utcnow().isoformat())),
                updated_at=datetime.fromisoformat(payload.get("updated_at", datetime.utcnow().isoformat()))
            )

        return None
    except JWTError:
        return None