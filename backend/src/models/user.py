from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship
import uuid
from sqlalchemy import String

# Use TYPE_CHECKING to avoid circular import issues
if TYPE_CHECKING:
    from .task import Task


class UserBase(SQLModel):
    """Base model for User containing common fields"""
    email: str = Field(unique=True, nullable=False, max_length=255)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """
    User model representing an authenticated user in the system

    Fields:
    - id: UUID primary key, auto-generated
    - email: Unique email address for authentication
    - password_hash: Hashed password using bcrypt or similar
    - created_at: Timestamp of account creation, auto-generated
    - updated_at: Timestamp of last update, auto-updated
    - is_active: Boolean indicating if account is active
    """
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, sa_column_kwargs={"name": "id"})
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to Task model
    tasks: list["Task"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str


class UserRead(UserBase):
    """Model for reading user data (without sensitive info)"""
    id: str
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    """Model for updating user information"""
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserLogin(SQLModel):
    """Model for user login credentials"""
    email: str
    password: str