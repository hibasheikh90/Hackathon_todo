#!/usr/bin/env python3
"""
Todo App - Phase I: Console Application

Entry point for the application.
This module initializes and runs the CLI interface with proper error handling.
"""

from .cli.menu import TodoCLI


def main() -> None:
    """Application entry point."""
    try:
        app = TodoCLI()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print("Please report this issue.\n")


if __name__ == "__main__":
    main()
