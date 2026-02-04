#!/usr/bin/env python3
"""Debug script to test database connection and authentication"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set the environment variable before importing the database module
os.environ['DATABASE_URL'] = 'sqlite:///./todo_app.db'

from src.database import DATABASE_URL, engine
from src.services.auth_service import AuthService
from src.models.user import UserCreate
from sqlalchemy.orm import Session

def test_database_connection():
    print(f"Using database URL: {DATABASE_URL}")

    try:
        # Test the connection
        with engine.begin() as conn:
            print("Database connection successful!")

        # Create a mock session to test AuthService
        from src.database import SessionLocal

        with SessionLocal() as session:
            auth_service = AuthService(session)

            # Try to register a test user
            user_data = UserCreate(email="test@example.com", password="testpassword123")
            print("Attempting to register test user...")

            try:
                created_user = auth_service.register_user(user_data)
                print(f"User created successfully: {created_user.email}")
            except Exception as e:
                print(f"User registration failed: {e}")

            # Now try to authenticate
            print("Attempting to authenticate user...")
            auth_result = auth_service.authenticate_user("test@example.com", "testpassword123")
            if auth_result:
                print(f"Authentication successful: {auth_result}")
            else:
                print("Authentication failed")

    except Exception as e:
        print(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()