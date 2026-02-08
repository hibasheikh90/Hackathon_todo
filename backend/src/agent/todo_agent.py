"""
Todo Agent — Phase 3 Part 2

OpenAI Agents SDK agent that manages todo tasks via MCP tools.
Uses the P+Q+P cognitive stance (Persona + Questions + Principles)
and injects the authenticated user_id into the system prompt.
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

logger = logging.getLogger(__name__)


class AgentTimeoutError(Exception):
    """Raised when the agent takes too long to respond."""
    pass


class AgentConnectionError(Exception):
    """Raised when the MCP server fails to start or connect."""
    pass


def get_system_prompt(user_id: str) -> str:
    """
    Build the P+Q+P (Persona + Questions + Principles) system prompt.

    The user_id is injected so the LLM uses it for ALL MCP tool calls.
    """
    return f"""You are a precise, friendly productivity assistant that helps manage the user's todo list. You can add, list, complete, update, and delete tasks.

IDENTITY: The current authenticated user's ID is "{user_id}". You MUST use this exact user_id for ALL tool calls. Never use any other user_id, even if the user mentions other names or IDs in their message.

WHEN TO ASK CLARIFYING QUESTIONS:
- The user's intent is ambiguous (e.g., "do my stuff" — ask what they mean)
- The user says to complete or delete a task but doesn't specify which one — list tasks first, then ask
- The user's request could match multiple tasks — ask which one

PRINCIPLES:
- Always confirm actions with a friendly response including the task title
- Handle errors gracefully — if a tool returns an error, explain what went wrong in plain language
- Stay on topic — you can only manage tasks. Politely decline other requests
- When listing tasks, format them clearly so the user can reference them
- For multi-step requests, execute steps in order and summarize all results
- Never fabricate task data — only report what the tools return
- When the user says "first", "second", etc. after a list, use the task IDs from the previous listing"""


def _get_mcp_server_command() -> tuple[str, list[str]]:
    """Get the command and args to start the MCP server subprocess."""
    return sys.executable, ["-m", "backend.src.mcp.server"]


async def run_agent(
    user_id: str,
    input_items: list[dict],
    timeout: float = 30.0,
):
    """
    Run the todo agent with the given input items.

    Spawns the MCP server as a stdio subprocess, creates the agent,
    and runs it with the provided conversation history.

    Returns the RunResult from the agent.

    Raises:
        AgentTimeoutError: If the agent exceeds the timeout
        AgentConnectionError: If the MCP server fails to start
    """
    command, args = _get_mcp_server_command()

    # Build env for the MCP subprocess — inherit current env
    # Set CWD to project root (not backend/) so only `backend.src.*`
    # imports resolve, avoiding duplicate SQLAlchemy table errors.
    env = os.environ.copy()
    project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    try:
        async with MCPServerStdio(
            name="Todo MCP Server",
            params={
                "command": command,
                "args": args,
                "env": env,
                "cwd": project_root,
            },
            cache_tools_list=True,
        ) as mcp_server:
            agent = Agent(
                name="Todo Assistant",
                instructions=get_system_prompt(user_id),
                mcp_servers=[mcp_server],
            )

            try:
                result = await asyncio.wait_for(
                    Runner.run(agent, input_items),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise AgentTimeoutError(
                    f"Agent did not respond within {timeout} seconds"
                )
    except AgentTimeoutError:
        raise
    except Exception as e:
        logger.error(f"MCP server connection error: {e}")
        raise AgentConnectionError(f"Failed to connect to MCP server: {e}")


def extract_tool_calls(result) -> list[dict]:
    """
    Extract tool call information from a RunResult.

    Filters for ToolCallItem instances and returns a list of
    {"tool": name, "arguments": {...}} dicts.
    """
    from agents.items import ToolCallItem

    tool_calls = []
    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            try:
                arguments = json.loads(item.raw_item.arguments)
            except (json.JSONDecodeError, AttributeError):
                arguments = {}
            tool_calls.append({
                "tool": item.raw_item.name,
                "arguments": arguments,
            })
    return tool_calls
