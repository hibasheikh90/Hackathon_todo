import re
from typing import Union
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import html
import logging

# Set up logging
logger = logging.getLogger(__name__)

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to sanitize and validate input data to prevent XSS and other injection attacks.
    """

    def __init__(self, app):
        super().__init__(app)

        # Define potentially dangerous patterns
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',               # JavaScript protocol
            r'on\w+\s*=',                # Event handlers (onclick, onload, etc.)
            r'<iframe[^>]*>.*?</iframe>', # iframe tags
            r'<object[^>]*>.*?</object>', # object tags
            r'<embed[^>]*>.*?</embed>',   # embed tags
            r'<link[^>]*>',              # link tags
            r'<meta[^>]*>',              # meta tags
        ]

        # Compile regex patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.dangerous_patterns]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Sanitize request data before passing to the next middleware/route handler.
        """
        # Sanitize query parameters
        if request.query_params:
            sanitized_query_params = {}
            has_dangerous_input = False

            for key, value in request.query_params.items():
                sanitized_value = self.sanitize_input(value)
                if sanitized_value != value:
                    has_dangerous_input = True
                    logger.warning(f"Dangerous input detected and sanitized in query param '{key}': {value}")

                sanitized_query_params[key] = sanitized_value

            # Replace the query params with sanitized versions
            if has_dangerous_input:
                # Create a new request with sanitized query parameters
                # For now, we'll log the issue - in a real implementation,
                # you might want to reject the request entirely
                pass

        # Sanitize path parameters (this is more complex and usually handled by FastAPI path validation)
        # Sanitize request body if it's JSON or form data

        # For now, we'll focus on logging and detection
        # In a production environment, you'd want to actually sanitize the body
        # which requires intercepting the request body before it's parsed

        response = await call_next(request)
        return response

    def sanitize_input(self, input_str: Union[str, None]) -> str:
        """
        Sanitize a single input string by removing or escaping dangerous patterns.

        Args:
            input_str: Input string to sanitize

        Returns:
            Sanitized string
        """
        if input_str is None:
            return input_str

        # First, escape HTML entities
        sanitized = html.escape(input_str)

        # Then, check for and remove dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(sanitized):
                # Log the dangerous input
                logger.warning(f"Dangerous pattern detected in input: {sanitized[:100]}...")
                # Remove the dangerous pattern
                sanitized = pattern.sub('', sanitized)

        return sanitized


def sanitize_string_field(field_value: Union[str, None], max_length: int = 1000) -> Union[str, None]:
    """
    Helper function to sanitize individual string fields.

    Args:
        field_value: Value to sanitize
        max_length: Maximum allowed length for the field

    Returns:
        Sanitized field value
    """
    if field_value is None:
        return field_value

    if not isinstance(field_value, str):
        raise TypeError("Field value must be a string or None")

    # Trim whitespace
    field_value = field_value.strip()

    # Check length
    if len(field_value) > max_length:
        raise ValueError(f"Field exceeds maximum length of {max_length} characters")

    # Escape HTML
    sanitized = html.escape(field_value)

    # Additional sanitization can be added here
    return sanitized