import sys
import os

# Compute key directories
_src_dir = os.path.dirname(os.path.abspath(__file__))        # backend/src/
_backend_dir = os.path.dirname(_src_dir)                      # backend/
_project_root = os.path.dirname(_backend_dir)                 # hackathon_todo/

# Add src/ for bare imports (database_hf, middleware, api, etc.)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)
# Add project root so backend.src.* imports used by sub-modules resolve
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Load .env BEFORE any imports that read DATABASE_URL at import time
from dotenv import load_dotenv
load_dotenv(os.path.join(_backend_dir, ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import logging

# Absolute imports from src
from middleware.input_sanitization import InputSanitizationMiddleware
from api.auth import router as auth_router
from api.tasks import router as tasks_router
from api.chat import router as chat_router
from api.chatkit_endpoint import router as chatkit_router
from database_hf import create_tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    app.include_router(chat_router, prefix="/api", tags=["Chat"])
    app.include_router(chatkit_router, prefix="/api", tags=["ChatKit"])

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


# # src/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from dotenv import load_dotenv
# import logging

# from backend.src.middleware.input_sanitization import InputSanitizationMiddleware
# from backend.src.api.auth import router as auth_router
# from backend.src.api.tasks import router as tasks_router
# from backend.src.database import create_tables

# # Load environment variables
# load_dotenv()

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Rate limiter
# limiter = Limiter(key_func=get_remote_address)

# # ------------------------
# # Top-level FastAPI app
# # ------------------------
# app = FastAPI(title="Todo API", version="1.0.0")

# # Middleware
# app.add_middleware(InputSanitizationMiddleware)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Routers
# app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])

# # Root endpoint
# @app.get("/")
# def read_root():
#     return {"message": "Todo API is running!"}

# # Startup event
# @app.on_event("startup")
# async def on_startup():
#     logger.info("Initializing database tables...")
#     try:
#         await create_tables()
#         logger.info("Database tables created successfully!")
#     except Exception as e:
#         logger.warning(f"Warning: Could not initialize database tables: {e}")
