"""
Chat API Endpoint — Phase 3 Part 2

POST /api/chat — Authenticated chat endpoint that orchestrates the
OpenAI Agents SDK agent with MCP tools for todo management.
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.src.database import get_async_session
from backend.src.models.user import User
from backend.src.dependencies.auth import get_current_user
from backend.src.services.chat_service import ChatService
from backend.src.agent.todo_agent import (
    run_agent,
    extract_tool_calls,
    AgentTimeoutError,
    AgentConnectionError,
)

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ToolCallInfo(BaseModel):
    tool: str
    arguments: dict


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: list[ToolCallInfo]


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Send a message and get an AI response with tool calls.

    The agent uses the authenticated user's ID for all MCP tool calls.
    Conversation state is persisted in the database.
    """
    # Validate OPENAI_API_KEY is configured
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "").startswith("sk-your-"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service configuration error",
        )

    chat_service = ChatService(db)

    # 1. Get or create conversation
    conversation = await chat_service.get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=chat_request.conversation_id,
    )

    # 2. Load conversation history
    history = await chat_service.get_conversation_history(conversation.id)

    # 3. Save user message
    await chat_service.save_message(
        conversation_id=conversation.id,
        role="user",
        content=chat_request.message,
    )

    # 4. Build input items (history + new message)
    input_items = ChatService.build_input_items(history)
    input_items.append({"role": "user", "content": chat_request.message})

    # 5. Run agent
    try:
        result = await run_agent(
            user_id=current_user.id,
            input_items=input_items,
        )
    except AgentTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI response timed out",
        )
    except AgentConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable",
        )
    except Exception as e:
        logger.error(f"Unexpected agent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    # 6. Extract response and tool calls
    response_text = result.final_output or "I couldn't generate a response. Please try again."
    tool_calls_list = extract_tool_calls(result)

    # 7. Save assistant message
    await chat_service.save_message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        tool_calls=tool_calls_list if tool_calls_list else None,
    )

    # 8. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=[
            ToolCallInfo(tool=tc["tool"], arguments=tc["arguments"])
            for tc in tool_calls_list
        ],
    )
