from typing import Optional, Dict
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.models.user import User, UserCreate, UserLogin
from backend.src.database.async_utils import async_user_crud


class AuthService:
    """
    Authentication service handling user registration, login, and JWT token management
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_for_dev")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a plain password"""
        return self.pwd_context.hash(password)

    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user with email and password

        Args:
            user_data: UserCreate object containing email and password

        Returns:
            User: The created user object

        Raises:
            ValueError: If email is already registered or invalid
        """
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_data.email):
            raise ValueError("Invalid email format")

        # Validate password strength
        if len(user_data.password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Check if user already exists
        existing_user = await async_user_crud.get_by_email(self.db, user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash the password
        hashed_password = self.get_password_hash(user_data.password)

        # Create the user with hashed password
        user = User(
            email=user_data.email,
            password_hash=hashed_password
        )

        # Save to database
        try:
            created_user = await async_user_crud.create(self.db, user)
            return created_user
        except Exception as e:
            raise ValueError(f"Failed to create user: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, str]]:
        """
        Authenticate a user with email and password

        Args:
            email: User's email address
            password: User's plain password

        Returns:
            Optional[Dict]: Dictionary containing access_token if authentication succeeds, None otherwise
        """
        # Get user from database
        user = await async_user_crud.get_by_email(self.db, email)

        if not user or not self.verify_password(password, user.password_hash):
            return None

        # Create access token
        access_token = self.create_access_token(data={"sub": str(user.id), "email": user.email})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token

        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """
        Create a JWT refresh token

        Args:
            data: Data to encode in the token

        Returns:
            str: Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify a JWT token and return its payload

        Args:
            token: JWT token to verify

        Returns:
            Optional[dict]: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    async def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Get user from JWT token

        Args:
            token: JWT token to decode

        Returns:
            Optional[User]: User object if token is valid and user exists, None otherwise
        """
        payload = self.verify_token(token)
        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        # Get user from database
        user = await async_user_crud.get_by_id(self.db, user_id)
        return user