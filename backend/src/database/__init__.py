from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker
import os
from contextlib import contextmanager


# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./todo_app.db"
)

# Sync engine
if "sqlite" in DATABASE_URL:
    # SQLite doesn't support the same connection parameters
    engine = create_engine(
        DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"),
        echo=False,
    )
else:
    # PostgreSQL/Neon parameters
    engine = create_engine(
        DATABASE_URL.replace("+asyncpg", "") if "+asyncpg" in DATABASE_URL else DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
    )


# Session maker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_sync_session() -> Session:
    """Get sync database session"""
    with SessionLocal() as session:
        yield session


def create_tables():
    """Create all tables in the database"""
    from sqlmodel import SQLModel
    from ..models.user import User
    from ..models.task import Task

    with engine.begin() as conn:
        SQLModel.metadata.create_all(bind=conn)


def drop_tables():
    """Drop all tables in the database (for testing)"""
    from sqlmodel import SQLModel

    with engine.begin() as conn:
        SQLModel.metadata.drop_all(bind=conn)

__all__ = ["get_sync_session", "create_tables", "drop_tables", "engine", "SessionLocal"]