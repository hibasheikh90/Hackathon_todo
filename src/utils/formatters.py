"""
String formatting utilities for the Todo application.

This module provides helper functions for formatting text and output.
"""


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text with ellipsis if too long.

    Args:
        text: The text to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated text with '...' if needed, or original text if within limit
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
