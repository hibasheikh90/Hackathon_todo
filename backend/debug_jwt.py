#!/usr/bin/env python3
"""Debug script to test JWT token creation and verification"""

import os
import uuid
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import select
from sqlalchemy.orm import Session

# Add the src directory to the path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.user import User
from src.database import get_sync_session
from src.services.auth_service import AuthService

def debug_jwt():
    print("Setting up environment...")
    os.environ["BETTER_AUTH_SECRET"] = "debug-secret-change-in-production"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

    # Create a mock database session (we'll use the actual database)
    from src.database import SessionLocal

    with SessionLocal() as db:
        print("Creating auth service...")
        auth_service = AuthService(db)

        # Create a test user
        print("Creating test user...")
        from src.models.user import UserCreate
        user_create = UserCreate(email="debug@example.com", password="password123")

        # First check if user exists and delete if so
        from src.database.utils import user_crud
        existing_user = user_crud.get_by_email_sync(db, "debug@example.com")
        if existing_user:
            print(f"Found existing user: {existing_user.id}")
            # Just use the existing user

        # Create or get user
        if not existing_user:
            test_user = User(
                email="debug@example.com",
                password_hash=auth_service.get_password_hash("password123")
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            user = test_user
            print(f"Created user: {user.id}, type: {type(user.id)}")
        else:
            user = existing_user
            print(f"Using existing user: {user.id}, type: {type(user.id)}")

        # Create token
        print("\nCreating token...")
        token_data = auth_service.authenticate_user("debug@example.com", "password123")
        if token_data:
            token = token_data["access_token"]
            print(f"Created token: {token[:30]}...")

            # Now try to decode and get user
            print("\nTrying to get user from token...")
            try:
                user_from_token = auth_service.get_user_from_token(token)
                print(f"Got user from token: {user_from_token.email if user_from_token else 'None'}")
            except Exception as e:
                print(f"Error getting user from token: {e}")

                # Let's manually decode the token to see what's inside
                try:
                    decoded_payload = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
                    print(f"Decoded payload: {decoded_payload}")
                    sub_value = decoded_payload.get("sub")
                    print(f"Sub value: {sub_value}, type: {type(sub_value)}")
                except Exception as decode_e:
                    print(f"Error decoding token manually: {decode_e}")
        else:
            print("Failed to authenticate user")

if __name__ == "__main__":
    debug_jwt()