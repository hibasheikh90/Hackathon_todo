from sqlmodel import create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as SQLAlchemyAsyncSession
from sqlalchemy.orm import sessionmaker
import os
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./todo_app.db"  # Use SQLite as default for Hugging Face Spaces
)

logger.info(f"Using database URL: {DATABASE_URL}")

# Determine if we're using SQLite (for Hugging Face Spaces) or PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    # For SQLite, use synchronous engine
    sync_engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}  # Required for SQLite in multithreaded environments
    )

    # For SQLite, we'll use a sync session for simplicity in Hugging Face Spaces
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine
    )

    # For async operations with SQLite, we'll create a mock async engine
    # In a real scenario, you might want to use aiosqlite for true async SQLite
    async_engine = None

    AsyncSessionLocal = None

else:
    # Process database URL to handle asyncpg-specific parameter issues
    def _process_db_url(url):
        """Process database URL to fix asyncpg compatibility issues."""
        if "+asyncpg" in url and "?" in url:
            base_url, params_str = url.split("?", 1)
            params = params_str.split("&")

            # Filter out parameters that cause issues with asyncpg
            filtered_params = []
            for param in params:
                if not param.startswith(('sslmode=', 'sslcert=', 'sslkey=', 'sslrootcert=')):
                    filtered_params.append(param)

            if filtered_params:
                return f"{base_url}?{'&'.join(filtered_params)}"
            else:
                return base_url
        return url

    # Process URLs for asyncpg compatibility
    ASYNC_DATABASE_URL = _process_db_url(DATABASE_URL)  # Process for async compatibility too
    SYNC_DATABASE_URL = _process_db_url(DATABASE_URL)  # Process for sync compatibility

    # PostgreSQL/Neon parameters only (Phase 2 requirement)
    # Process URLs for compatibility
    sync_db_url = SYNC_DATABASE_URL.replace("+asyncpg", "")
    async_db_url = ASYNC_DATABASE_URL  # Processed for asyncpg compatibility

    sync_engine = create_engine(
        sync_db_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
    )

    # Async engine for PostgreSQL - use URL that's safe for asyncpg
    async_engine = create_async_engine(
        async_db_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
    )

    # Session makers
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine
    )

    AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
        bind=async_engine
    )


def get_sync_session() -> Session:
    """Get sync database session"""
    with SessionLocal() as session:
        yield session


async def create_tables():
    """Create all tables in the database"""
    from sqlmodel import SQLModel
    from .models.user import User
    from .models.task import Task
    from .models.conversation import Conversation
    from .models.message import Message

    if DATABASE_URL.startswith("sqlite"):
        # For SQLite, use sync engine
        with sync_engine.begin() as conn:
            SQLModel.metadata.create_all(bind=conn)
    else:
        # For PostgreSQL, use async engine
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)


def drop_tables():
    """Drop all tables in the database (for testing)"""
    from sqlmodel import SQLModel
    from .models.user import User
    from .models.task import Task

    with sync_engine.begin() as conn:
        SQLModel.metadata.drop_all(bind=conn)


async def get_async_session():
    """Get async database session"""
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session
    else:
        # Fallback for SQLite - return a sync session wrapped as async
        # This is a workaround for Hugging Face Spaces with SQLite
        with SessionLocal() as session:
            yield session