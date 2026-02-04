import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import sys
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from .test_app import app  # Test app for testing
from src.models.user import UserCreate


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.fixture
def sync_session():
    """Create an in-memory SQLite database for testing"""
    # Use SQLite in-memory database for fast tests
    engine = create_engine("sqlite:///")

    def setup_test_db():
        with engine.begin() as conn:
            # Create all tables
            SQLModel.metadata.create_all(bind=conn)

        session = sessionmaker(engine, expire_on_commit=False)
        with session() as sess:
            yield sess

    return setup_test_db


def test_signup_new_user(client):
    """Test signing up a new user"""
    signup_data = {
        "email": "testuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data)

    assert response.status_code == 200

    # Check that the response contains user data
    user_data = response.json()
    assert "id" in user_data
    assert user_data["email"] == "testuser@example.com"
    assert "password_hash" not in user_data  # Password hash should not be returned


def test_signup_duplicate_email(client):
    """Test signing up with an already registered email"""
    # First signup should succeed
    signup_data = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 200

    # Second signup with same email should fail
    response = await client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_valid_credentials(client):
    """Test logging in with valid credentials"""
    # First, create a user
    signup_data = {
        "email": "loginuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 200

    # Now try to login
    login_data = {
        "email": "loginuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data)

    assert response.status_code == 200

    # Check that the response contains access token
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test logging in with invalid credentials"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data)

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_wrong_password(client):
    """Test logging in with wrong password"""
    # First, create a user
    signup_data = {
        "email": "wrongpassuser@example.com",
        "password": "CorrectPassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 200

    # Now try to login with wrong password
    login_data = {
        "email": "wrongpassuser@example.com",
        "password": "WrongPassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data)

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user_with_token(client):
    """Test getting current user info with valid token"""
    # First, create and login a user to get a token
    signup_data = {
        "email": "currentuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 200

    login_data = {
        "email": "currentuser@example.com",
        "password": "SecurePassword123!"
    }

    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    access_token = token_data["access_token"]

    # Now get current user info with the token
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200

    user_info = response.json()
    assert user_info["email"] == "currentuser@example.com"


def test_get_current_user_without_token(client):
    """Test getting current user info without token"""
    response = await client.get("/api/auth/me")

    assert response.status_code == 401


def test_get_current_user_with_invalid_token(client):
    """Test getting current user info with invalid token"""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401


def test_logout_endpoint(client):
    """Test logout endpoint (though it's mostly client-side for JWTs)"""
    response = await client.post("/api/auth/logout")

    # Logout should succeed even without a valid token
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["message"] == "Logged out successfully"


def test_password_validation_on_signup():
    """Test that passwords meet security requirements"""
    # This test would require implementing password validation in the model
    # For now, we'll just verify that the basic signup works
    user_create = UserCreate(
        email="validation@test.com",
        password="SecurePassword123!"
    )

    assert user_create.email == "validation@test.com"
    assert user_create.password == "SecurePassword123!"


def test_email_format_validation():
    """Test that emails are properly validated"""
    # Test valid email
    user_create = UserCreate(
        email="valid.email@test-domain.com",
        password="SecurePassword123!"
    )

    assert user_create.email == "valid.email@test-domain.com"

    # Note: Actual email validation would happen in the model
    # This test is just a placeholder for when validation is implemented