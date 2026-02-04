#!/usr/bin/env python3
"""
Database initialization script for the Todo application.

This script creates all required database tables based on the SQLModel definitions.
It can be run standalone to set up the database schema.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import create_tables, async_engine
from sqlmodel import SQLModel


async def init_db():
    """Initialize the database by creating all tables."""
    print("Initializing database...")

    try:
        # Import models to ensure they're registered with SQLModel
        from src.models.user import User
        from src.models.task import Task

        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        print("Database initialized successfully!")
        print("Tables created:")
        print("- users")
        print("- tasks")

    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

    return True


async def drop_db():
    """Drop all database tables (use with caution!)."""
    print("WARNING: Dropping all database tables...")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled.")
        return False

    try:
        from src.models.user import User
        from src.models.task import Task

        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

        print("All tables dropped successfully!")

    except Exception as e:
        print(f"Error dropping database: {e}")
        return False

    return True


async def check_connection():
    """Check if we can connect to the database."""
    try:
        from sqlalchemy.ext.asyncio import AsyncConnection

        async with async_engine.connect() as conn:
            # Execute a simple query to test the connection
            result = await conn.execute("SELECT 1")
            row = result.fetchone()

            if row:
                print("Database connection successful!")
                return True
            else:
                print("Database connection failed!")
                return False

    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


async def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python init_db.py [init|drop|check]")
        print("  init  - Initialize the database (create tables)")
        print("  drop  - Drop all tables (CAUTION: This will delete all data!)")
        print("  check - Check database connection")
        return 1

    command = sys.argv[1].lower()

    if command == "init":
        success = await init_db()
        return 0 if success else 1
    elif command == "drop":
        success = await drop_db()
        return 0 if success else 1
    elif command == "check":
        success = await check_connection()
        return 0 if success else 1
    else:
        print(f"Unknown command: {command}")
        print("Usage: python init_db.py [init|drop|check]")
        return 1


if __name__ == "__main__":
    # Set the event loop policy for Windows compatibility
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    exit_code = asyncio.run(main())
    sys.exit(exit_code)