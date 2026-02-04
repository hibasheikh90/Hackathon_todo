from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)

def add_rate_limiting(app: FastAPI):
    """
    Add rate limiting to the FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Add the rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add rate limits to specific endpoints
    # For example, limit authentication endpoints more strictly
    auth_limiter = limiter.shared_limit("5/minute", scope="auth")

    return limiter