import sys
import os

# backend/main.py se src folder ka path add kar rahe hain
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
from database import create_tables



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)

def create_app() -> FastAPI:
    app = FastAPI(title="Todo API", version="1.0.0")

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
        return {"message": "Todo API is running!"}

    @app.on_event("startup")
    async def on_startup():
        logger.info("Initializing database tables...")
        try:
            await create_tables()
            logger.info("Database tables created successfully!")
        except Exception as e:
            logger.warning(f"Warning: Could not initialize database tables: {e}")
            # Continue startup even if DB initialization fails (for cases like connection issues)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
