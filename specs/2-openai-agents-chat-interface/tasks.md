# Tasks: Phase 3 Part 2 — OpenAI Agents SDK and Auth Integration

**Feature**: OpenAI Agents SDK Chat Interface
**Feature Branch**: `2-openai-agents-chat-interface`
**Created**: 2026-02-08
**Status**: Complete
**Spec**: [specs/2-openai-agents-chat-interface/spec.md](spec.md)
**Plan**: [specs/2-openai-agents-chat-interface/plan.md](plan.md)

## Phase 1: Dependency & Scaffold

### Goal
Install the OpenAI Agents SDK dependency and create the new package directories (`agents/`).

### Independent Test
`python -c "from agents import Agent, Runner; print('OK')"` succeeds, and `python -c "from agents.mcp import MCPServerStdio; print('OK')"` succeeds.

### Implementation Tasks

- [x] T001 Add `openai-agents>=0.8.0` to `backend/requirements.txt` and install it
  - **Precondition**: `backend/requirements.txt` exists
  - **Artifacts**: `backend/requirements.txt`
  - **Ref**: Plan Step 1

- [x] T002 Create `backend/src/agents/__init__.py` with empty package init
  - **Precondition**: `backend/src/` directory exists
  - **Artifacts**: `backend/src/agents/__init__.py`
  - **Ref**: Plan Step 4, Spec File Structure

- [x] T003 Add `OPENAI_API_KEY` to `backend/.env` (placeholder) and verify it is loaded by dotenv
  - **Precondition**: `backend/.env` exists
  - **Artifacts**: `backend/.env`
  - **Ref**: Plan Step 1, Integration Points

## Phase 2: Database Models — Conversation & Message

### Goal
Create the Conversation and Message SQLModel models so the chat system can persist conversation state.

### Independent Test
Start the FastAPI server — the `conversations` and `messages` tables are auto-created by `create_tables()`. Verify with a direct SQL query or by importing the models and checking `__tablename__`.

### Implementation Tasks

- [x] T004 Create `backend/src/models/conversation.py` — `Conversation(SQLModel, table=True)` with fields: `id` (str, UUID PK, default uuid4), `user_id` (str, FK to users.id, indexed, NOT NULL), `created_at` (datetime, auto), `updated_at` (datetime, auto). Follow the same pattern as `Task` model for field defaults and column definitions.
  - **Precondition**: T001
  - **Artifacts**: `backend/src/models/conversation.py`
  - **Ref**: Plan Step 2, FR-007, Spec US6

- [x] T005 Create `backend/src/models/message.py` — `Message(SQLModel, table=True)` with fields: `id` (str, UUID PK, default uuid4), `conversation_id` (str, FK to conversations.id, indexed, NOT NULL), `role` (str, NOT NULL, one of "user"|"assistant"), `content` (str, NOT NULL), `tool_calls` (str, nullable, JSON string), `created_at` (datetime, auto). Follow the same pattern as `Task` model.
  - **Precondition**: T004
  - **Artifacts**: `backend/src/models/message.py`
  - **Ref**: Plan Step 2, FR-008, Spec US2

- [x] T006 Update `backend/src/models/__init__.py` to export `Conversation` and `Message` so they are registered with SQLModel metadata and auto-created by `create_tables()`
  - **Precondition**: T004, T005
  - **Artifacts**: `backend/src/models/__init__.py`
  - **Ref**: Plan Step 2

## Phase 3: Chat Service — Conversation CRUD

### Goal
Implement the service layer for managing conversations and messages, and for building agent input from message history.

### Independent Test
Create a conversation for a user, save 3 messages, retrieve history — verify all 3 messages returned in `created_at` order. Verify ownership check rejects a different user's conversation_id.

### Implementation Tasks

- [x] T007 Implement `get_or_create_conversation(db, user_id, conversation_id?)` in `backend/src/services/chat_service.py` — If `conversation_id` is None, create a new Conversation with generated UUID and return it. If provided, query by id AND user_id — return the conversation or raise an HTTPException(404) if not found or not owned.
  - **Precondition**: T006
  - **Artifacts**: `backend/src/services/chat_service.py`
  - **Ref**: Plan Step 3, FR-009, FR-010, Spec US2 Scenario 4

- [x] T008 Implement `get_conversation_history(db, conversation_id)` in `chat_service.py` — Query all Message records for the given `conversation_id`, ordered by `created_at` ASC. Return list[Message].
  - **Precondition**: T007
  - **Artifacts**: `backend/src/services/chat_service.py`
  - **Ref**: Plan Step 3, FR-012

- [x] T009 Implement `save_message(db, conversation_id, role, content, tool_calls?)` in `chat_service.py` — Create and persist a new Message record. Also update the parent Conversation's `updated_at` timestamp. Return the created Message.
  - **Precondition**: T007
  - **Artifacts**: `backend/src/services/chat_service.py`
  - **Ref**: Plan Step 3, FR-011

- [x] T010 Implement `build_input_items(messages, max_messages=50)` in `chat_service.py` — Convert a list of Message records to the OpenAI Agents SDK input format: `[{"role": "user"|"assistant", "content": "..."}]`. If len(messages) > max_messages, truncate the oldest messages keeping the most recent `max_messages`. Return list[dict].
  - **Precondition**: T008
  - **Artifacts**: `backend/src/services/chat_service.py`
  - **Ref**: Plan Step 3, FR-012, Edge Case (context window overflow)

## Phase 4: Agent Definition — P+Q+P Cognitive Stance

### Goal
Create the todo agent module with dynamic system prompt (P+Q+P pattern) and the `run_agent()` function that spawns the MCP server and executes the agent.

### Independent Test
Call `get_system_prompt("test-user-123")` and verify the returned string contains "test-user-123". Call `run_agent("test-user-123", [{"role": "user", "content": "Show me my tasks"}])` and verify it returns a `RunResult` with `final_output` (requires `OPENAI_API_KEY` and database).

### Implementation Tasks

- [x] T011 [US4] Implement `get_system_prompt(user_id: str) -> str` in `backend/src/agents/todo_agent.py` — Returns the P+Q+P system prompt string with the authenticated `user_id` injected. The prompt MUST include: (1) **Persona**: productivity assistant for todo management, (2) **Identity**: "The current authenticated user's ID is {user_id}. You MUST use this exact user_id for ALL tool calls.", (3) **Questions**: when to ask clarifying questions, (4) **Principles**: confirm actions, handle errors gracefully, stay on topic, never fabricate data, format task lists clearly.
  - **Precondition**: T002
  - **Artifacts**: `backend/src/agents/todo_agent.py`
  - **Ref**: Plan Step 4, FR-005, FR-006, Spec US4, ADR-005

- [x] T012 [US1, US3] Implement `run_agent(user_id: str, input_items: list[dict]) -> RunResult` in `todo_agent.py` — (1) Open `MCPServerStdio` context with `command="python"`, `args=["-m", "backend.src.mcp.server"]`, `cache_tools_list=True`. (2) Create `Agent(name="Todo Assistant", instructions=get_system_prompt(user_id), mcp_servers=[server])`. (3) Call `Runner.run(agent, input_items)` wrapped in `asyncio.wait_for(timeout=30)`. (4) Return the `RunResult`. Handle `TimeoutError` → raise a custom exception. Handle `MCPServerStdio` connection failure → raise a custom exception.
  - **Precondition**: T011
  - **Artifacts**: `backend/src/agents/todo_agent.py`
  - **Ref**: Plan Step 4, FR-004, FR-013, Spec US1

- [x] T013 Implement `extract_tool_calls(result: RunResult) -> list[dict]` in `todo_agent.py` — Iterate `result.new_items`, filter for `ToolCallItem` instances, extract `{"tool": item.raw_item.name, "arguments": json.loads(item.raw_item.arguments)}` for each. Return list of dicts.
  - **Precondition**: T012
  - **Artifacts**: `backend/src/agents/todo_agent.py`
  - **Ref**: Plan Step 6, FR-003

## Phase 5: Chat API Endpoint

### Goal
Create the `POST /api/chat` endpoint that wires together auth, conversation CRUD, agent execution, and message persistence.

### Independent Test
`POST /api/chat` with valid JWT and `{"message": "Show me my tasks"}` → returns `{"conversation_id": "...", "response": "...", "tool_calls": [...]}` with HTTP 200. Without JWT → HTTP 401. With empty message → HTTP 422.

### Implementation Tasks

- [x] T014 [US1, US3] Create `backend/src/api/chat.py` with request/response models — `ChatRequest(message: str, conversation_id: str | None)`, `ToolCallInfo(tool: str, arguments: dict)`, `ChatResponse(conversation_id: str, response: str, tool_calls: list[ToolCallInfo])`. Create router with `APIRouter(prefix="/api", tags=["chat"])`.
  - **Precondition**: T010, T013
  - **Artifacts**: `backend/src/api/chat.py`
  - **Ref**: Plan Step 5, FR-001, FR-003

- [x] T015 [US1, US2, US3] Implement the `POST /api/chat` endpoint body — Full orchestration loop: (1) Validate message non-empty, (2) `get_or_create_conversation(db, user.id, conversation_id)`, (3) `get_conversation_history(db, conversation.id)`, (4) `save_message(db, conversation.id, "user", message)`, (5) `build_input_items(history + new message)`, (6) `run_agent(user.id, input_items)`, (7) Extract `result.final_output` + `extract_tool_calls(result)`, (8) `save_message(db, conversation.id, "assistant", response, tool_calls_json)`, (9) Return `ChatResponse`. Rate limit: `@limiter.limit("20/minute")`. Auth: `Depends(get_current_user)`.
  - **Precondition**: T014
  - **Artifacts**: `backend/src/api/chat.py`
  - **Ref**: Plan Step 5-6, FR-001, FR-002, FR-011, FR-012, FR-015, Spec US1-US3

- [x] T016 Register the chat router in `backend/src/main.py` — Import `chat_router` from `backend.src.api.chat` and add `app.include_router(chat_router)`
  - **Precondition**: T015
  - **Artifacts**: `backend/src/main.py`
  - **Ref**: Plan Step 5

## Phase 6: Error Handling & Hardening

### Goal
Ensure all error paths return appropriate HTTP status codes and user-friendly messages, and edge cases are handled gracefully.

### Independent Test
Test each error path: no JWT → 401, expired JWT → 401, invalid conversation_id → 404, empty message → 422, MCP failure → 503, agent timeout → 504. Verify no raw stack traces leak to the client.

### Implementation Tasks

- [x] T017 [US3] Add error handling to the chat endpoint — Catch and map: `TimeoutError` → HTTP 504 "AI response timed out", MCP connection failure → HTTP 503 "AI service temporarily unavailable", missing `OPENAI_API_KEY` → HTTP 503 "AI service configuration error", unexpected exceptions → HTTP 500 with logged traceback but user-friendly response. Verify JWT errors (401) are handled by existing `get_current_user` dependency.
  - **Precondition**: T015
  - **Artifacts**: `backend/src/api/chat.py`
  - **Ref**: Plan Step 8, FR-014, Spec Edge Cases

- [x] T018 Add input validation — Validate `message` field is non-empty string (not just whitespace). Validate `conversation_id` format if provided (must be valid UUID). Return HTTP 422 with clear error messages for validation failures.
  - **Precondition**: T014
  - **Artifacts**: `backend/src/api/chat.py`
  - **Ref**: Plan Step 8, Spec Edge Case (empty message)

## Phase 7: Integration Testing

### Goal
Validate the complete chat pipeline end-to-end with automated tests covering auth, conversation persistence, agent behavior, and error cases.

### Independent Test
`pytest backend/tests/test_chat_endpoint.py backend/tests/test_agent.py backend/tests/test_conversation_model.py` — all tests pass.

### Implementation Tasks

- [x] T019 Create `backend/tests/test_conversation_model.py` — Test Conversation CRUD: create conversation, verify fields (id, user_id, timestamps). Test Message CRUD: create messages, verify ordering by created_at. Test user isolation: query conversation with wrong user_id returns None.
  - **Precondition**: T006
  - **Artifacts**: `backend/tests/test_conversation_model.py`
  - **Ref**: Plan Step 7, SC-005

- [x] T020 [US3] Create `backend/tests/test_agent.py` — Test `get_system_prompt()` contains injected user_id. Test that the system prompt includes P+Q+P elements (persona, questions guidance, principles). Test `extract_tool_calls()` correctly parses ToolCallItem objects.
  - **Precondition**: T013
  - **Artifacts**: `backend/tests/test_agent.py`
  - **Ref**: Plan Step 7, SC-002

- [x] T021 [US1, US2, US3, US5] Create `backend/tests/test_chat_endpoint.py` — Test authenticated request returns valid ChatResponse (conversation_id, response, tool_calls). Test unauthenticated request returns 401. Test new conversation creation (no conversation_id → new UUID returned). Test existing conversation continuation (same conversation_id → messages accumulate). Test conversation ownership (user A cannot use user B's conversation_id → 404). Test empty message → 422.
  - **Precondition**: T017
  - **Artifacts**: `backend/tests/test_chat_endpoint.py`
  - **Ref**: Plan Step 7, SC-001, SC-003, SC-004, SC-005

- [x] T022 Update `backend/tests/conftest.py` — Add fixtures for creating test conversations and messages. Add fixture for authenticated test client with valid JWT. Ensure new model tables are created in test database.
  - **Precondition**: T006
  - **Artifacts**: `backend/tests/conftest.py`
  - **Ref**: Plan Step 7

## Dependencies

### Task Completion Order
1. T001-T003: Scaffold (sequential)
2. T004-T006: Database models (sequential — Message FK depends on Conversation)
3. T007-T010: Chat service (sequential — each builds on prior)
4. T011-T013: Agent definition (sequential — run_agent needs system prompt, extract needs RunResult)
5. T014-T016: API endpoint (depends on Phase 3 + Phase 4)
6. T017-T018: Error handling (depends on T015)
7. T019-T022: Testing (depends on respective implementation tasks)

### Critical Path
T001 → T004 → T006 → T007 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017

### Parallel Execution
- T002 and T003 can run in parallel with T001 (independent setup tasks)
- T019 and T022 can start after T006 (model tests don't need agent)
- T020 can start after T013 (agent unit tests)
- T017 and T018 can run in parallel (both modify chat.py but different concerns)

## Success Criteria Mapping

| Success Criterion | Validated By |
|-------------------|-------------|
| SC-001: Chat response <30s p95 | T012 (timeout), T021 |
| SC-002: user_id from JWT in 100% of MCP calls | T011, T020 |
| SC-003: Unauthenticated → 401 | T017, T021 |
| SC-004: Multi-turn context maintained | T015, T021 |
| SC-005: Conversation/message persisted | T019, T021 |
| SC-006: Multi-step tool chaining | T012, T021 |
| SC-007: MCP subprocess starts successfully | T012 |
| SC-008: Errors return correct HTTP codes | T017, T021 |
