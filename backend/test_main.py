import sys
import os

# backend/test_main.py - modified version for testing with in-memory database
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import asyncio
import logging

# Correct imports from src folder
from middleware.input_sanitization import InputSanitizationMiddleware
from api.auth import router as auth_router
from api.tasks import router as tasks_router

# For testing purposes, we'll create a function to create tables with an in-memory DB
async def create_test_tables():
    """Create tables for testing with in-memory database"""
    from sqlmodel import SQLModel, create_engine
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    from sqlmodel.ext.asyncio.session import AsyncSession

    # Use in-memory SQLite for testing
    test_database_url = "sqlite+aiosqlite:///:memory:"

    # Create test engines
    sync_engine = create_engine("sqlite:///./test.db")  # Using file for testing
    async_engine = create_async_engine(test_database_url)

    from src.models.user import User
    from src.models.task import Task

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Replace the global engines temporarily
    import src.database as db_module
    original_async_engine = db_module.async_engine
    original_sync_engine = db_module.sync_engine
    original_AsyncSessionLocal = db_module.AsyncSessionLocal
    original_SessionLocal = db_module.SessionLocal

    # Update the database module with test engines
    db_module.async_engine = async_engine
    db_module.sync_engine = sync_engine
    db_module.AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
        bind=async_engine
    )
    db_module.SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine
    )

    return original_async_engine, original_sync_engine, original_AsyncSessionLocal, original_SessionLocal


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)

def create_test_app() -> FastAPI:
    app = FastAPI(title="Todo API - Test Mode", version="1.0.0")

    # Add input sanitization middleware (should be first in the chain)
    app.add_middleware(InputSanitizationMiddleware)

    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this to your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])

    @app.get("/")
    def read_root():
        return {"message": "Todo API is running in test mode!"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "database": "using test database"}

    @app.on_event("startup")
    async def on_startup():
        logger.info("Initializing test database tables...")
        try:
            # Create test tables with in-memory database
            await create_test_tables()
            logger.info("Test database tables created successfully!")
        except Exception as e:
            logger.error(f"Error initializing test database: {e}")
            # Continue startup even if DB initialization fails

    return app


app = create_test_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)