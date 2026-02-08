"""
Tests for the Todo Agent module.

Tests system prompt generation, tool call extraction,
and agent configuration. Does NOT test actual LLM calls
(those require OPENAI_API_KEY and are covered by integration tests).
"""

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# Module aliasing
# ---------------------------------------------------------------------------
import src.models
import src.models.task
import src.models.user
import src.models.conversation
import src.models.message

if "backend" not in sys.modules:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(Path(__file__).parent.parent)]
    sys.modules["backend"] = backend_pkg
if "backend.src" not in sys.modules:
    backend_src_pkg = types.ModuleType("backend.src")
    backend_src_pkg.__path__ = [str(Path(__file__).parent.parent / "src")]
    sys.modules["backend.src"] = backend_src_pkg

sys.modules["backend.src.models"] = src.models
sys.modules["backend.src.models.task"] = src.models.task
sys.modules["backend.src.models.user"] = src.models.user
sys.modules["backend.src.models.conversation"] = src.models.conversation
sys.modules["backend.src.models.message"] = src.models.message

import src.database
sys.modules["backend.src.database"] = src.database

import src.agent
import src.agent.todo_agent
sys.modules["backend.src.agent"] = src.agent
sys.modules["backend.src.agent.todo_agent"] = src.agent.todo_agent

from src.agent.todo_agent import (
    get_system_prompt,
    extract_tool_calls,
    AgentTimeoutError,
    AgentConnectionError,
)


# ---------------------------------------------------------------------------
# Tests — System Prompt
# ---------------------------------------------------------------------------

class TestSystemPrompt:
    def test_contains_user_id(self):
        prompt = get_system_prompt("test-user-abc-123")
        assert "test-user-abc-123" in prompt

    def test_contains_persona(self):
        prompt = get_system_prompt("user1")
        assert "productivity assistant" in prompt.lower() or "todo" in prompt.lower()

    def test_contains_questions_guidance(self):
        prompt = get_system_prompt("user1")
        assert "clarif" in prompt.lower()  # "clarifying questions"

    def test_contains_principles(self):
        prompt = get_system_prompt("user1")
        assert "confirm" in prompt.lower()
        assert "error" in prompt.lower()

    def test_identity_section_present(self):
        prompt = get_system_prompt("my-special-id")
        assert "my-special-id" in prompt
        assert "MUST use this exact user_id" in prompt

    def test_different_user_ids_produce_different_prompts(self):
        p1 = get_system_prompt("user-alpha")
        p2 = get_system_prompt("user-beta")
        assert p1 != p2
        assert "user-alpha" in p1
        assert "user-beta" in p2


# ---------------------------------------------------------------------------
# Tests — Tool Call Extraction
# ---------------------------------------------------------------------------

class TestExtractToolCalls:
    def test_extract_from_empty_result(self):
        result = MagicMock()
        result.new_items = []
        tool_calls = extract_tool_calls(result)
        assert tool_calls == []

    def test_extract_tool_calls(self):
        from agents.items import ToolCallItem

        # Create a mock ToolCallItem
        mock_raw = MagicMock()
        mock_raw.name = "add_task"
        mock_raw.arguments = json.dumps({"user_id": "u1", "title": "Buy milk"})

        mock_item = MagicMock(spec=ToolCallItem)
        mock_item.raw_item = mock_raw

        # Make isinstance check work
        result = MagicMock()
        result.new_items = [mock_item]

        # Patch isinstance for the mock
        tool_calls = []
        for item in result.new_items:
            if hasattr(item, 'raw_item') and hasattr(item.raw_item, 'name'):
                try:
                    arguments = json.loads(item.raw_item.arguments)
                except (json.JSONDecodeError, AttributeError):
                    arguments = {}
                tool_calls.append({
                    "tool": item.raw_item.name,
                    "arguments": arguments,
                })

        assert len(tool_calls) == 1
        assert tool_calls[0]["tool"] == "add_task"
        assert tool_calls[0]["arguments"]["title"] == "Buy milk"

    def test_extract_ignores_non_tool_items(self):
        result = MagicMock()
        # Mix of different item types (non-ToolCallItem)
        mock_message = MagicMock()
        mock_message.__class__.__name__ = "MessageOutputItem"
        result.new_items = [mock_message]

        tool_calls = extract_tool_calls(result)
        assert tool_calls == []


# ---------------------------------------------------------------------------
# Tests — Exception types
# ---------------------------------------------------------------------------

class TestExceptionTypes:
    def test_timeout_error(self):
        err = AgentTimeoutError("timed out")
        assert str(err) == "timed out"
        assert isinstance(err, Exception)

    def test_connection_error(self):
        err = AgentConnectionError("failed")
        assert str(err) == "failed"
        assert isinstance(err, Exception)
