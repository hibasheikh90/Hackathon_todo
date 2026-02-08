"""
TodoChatKitServer — Phase 3 Part 3

ChatKitServer subclass that integrates with the existing OpenAI Agents SDK
agent and MCP tools. Uses the DatabaseChatKitStore for conversation persistence.
"""

import logging
from collections.abc import AsyncIterator
from datetime import datetime

from chatkit.server import ChatKitServer
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    UserMessageItem,
)

from backend.src.agent.todo_agent import (
    run_agent,
    AgentTimeoutError,
    AgentConnectionError,
)
from backend.src.chatkit.store import DatabaseChatKitStore

logger = logging.getLogger(__name__)

ThreadStreamEvent = (
    ThreadItemDoneEvent
    # The full union is handled by the type annotation from ChatKitServer
)


class TodoChatKitServer(ChatKitServer[dict]):
    """
    ChatKit server that delegates to the existing Todo Agent.

    The respond() method:
    1. Loads thread items from the store
    2. Converts them to agent input format
    3. Runs the agent with MCP tools
    4. Streams back the response with tool call annotations
    """

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator:
        user_id = context.get("user_id", "")
        if not user_id:
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.utcnow(),
                    content=[
                        AssistantMessageContent(
                            text="Authentication error. Please log in again.",
                        )
                    ],
                ),
            )
            return

        # Load thread history and convert to agent input format
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=50,
            order="asc",
            context=context,
        )

        input_items = []
        for item in items_page.data:
            if isinstance(item, UserMessageItem):
                texts = []
                for c in item.content:
                    if hasattr(c, "text"):
                        texts.append(c.text)
                if texts:
                    input_items.append({"role": "user", "content": " ".join(texts)})
            elif isinstance(item, AssistantMessageItem):
                texts = []
                for c in item.content:
                    if hasattr(c, "text"):
                        texts.append(c.text)
                if texts:
                    input_items.append(
                        {"role": "assistant", "content": " ".join(texts)}
                    )

        # Run the agent
        try:
            result = await run_agent(user_id=user_id, input_items=input_items)
        except AgentTimeoutError:
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.utcnow(),
                    content=[
                        AssistantMessageContent(
                            text="The AI took too long to respond. Please try a simpler request.",
                        )
                    ],
                ),
            )
            return
        except AgentConnectionError:
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.utcnow(),
                    content=[
                        AssistantMessageContent(
                            text="AI assistant is temporarily unavailable. Please try again later.",
                        )
                    ],
                ),
            )
            return
        except Exception as e:
            logger.error(f"Unexpected agent error: {e}")
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.utcnow(),
                    content=[
                        AssistantMessageContent(
                            text="Something went wrong. Please try again.",
                        )
                    ],
                ),
            )
            return

        # Extract response
        response_text = (
            result.final_output
            or "I couldn't generate a response. Please try again."
        )

        # Yield the response
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=thread.id,
                id=self.store.generate_item_id("message", thread, context),
                created_at=datetime.utcnow(),
                content=[
                    AssistantMessageContent(
                        text=response_text,
                    )
                ],
            ),
        )


def create_chatkit_server() -> TodoChatKitServer:
    """Create and return a configured TodoChatKitServer instance."""
    store = DatabaseChatKitStore()
    return TodoChatKitServer(store=store)
