"""
ChatKit API Endpoint — Phase 3 Part 3

POST /api/chatkit — Authenticated ChatKit endpoint that serves the
self-hosted ChatKit server with streaming responses.
"""

import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.src.database import get_async_session
from backend.src.models.user import User
from backend.src.dependencies.auth import get_current_user
from backend.src.chatkit.server import create_chatkit_server, TodoChatKitServer
from chatkit.server import StreamingResult

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["ChatKit"])

# Create server instance (reused across requests)
_chatkit_server: TodoChatKitServer | None = None


def get_chatkit_server() -> TodoChatKitServer:
    global _chatkit_server
    if _chatkit_server is None:
        _chatkit_server = create_chatkit_server()
    return _chatkit_server


@router.post("/chatkit")
@limiter.limit("20/minute")
async def chatkit_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    ChatKit server endpoint for streaming chat responses.

    Accepts ChatKit protocol requests, authenticates via JWT,
    and delegates to the TodoChatKitServer which runs the AI agent.
    """
    # Validate OPENAI_API_KEY is configured
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-your-"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service configuration error",
        )

    body = await request.body()
    server = get_chatkit_server()

    result = await server.process(
        body,
        context={"user_id": current_user.id},
    )

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
