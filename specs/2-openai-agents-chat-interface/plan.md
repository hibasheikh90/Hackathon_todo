# Implementation Plan: Phase 3 Part 2 — OpenAI Agents SDK and Auth Integration

**Branch**: `2-openai-agents-chat-interface` | **Date**: 2026-02-08 | **Spec**: `specs/2-openai-agents-chat-interface/spec.md`
**Input**: Feature specification from `specs/2-openai-agents-chat-interface/spec.md`

## Summary

Build an AI chat interface powered by the OpenAI Agents SDK (`openai-agents` package) that orchestrates natural language todo management through the Phase 3 Part 1 MCP server. The system implements a stateless `POST /api/chat` endpoint that authenticates users via existing JWT, spawns the MCP server as a stdio subprocess, runs an agent with conversation history from the database, and persists all messages. The agent uses a P+Q+P cognitive stance to remain a reliable, task-focused productivity assistant.

## Technical Context

**Language/Version**: Python 3.13+ (matching Phase 2)
**Primary Dependencies**: `openai-agents>=0.8.0` (OpenAI Agents SDK with MCP support), existing `mcp[cli]`, `sqlmodel`, `asyncpg`, `python-jose`
**Storage**: Neon Serverless PostgreSQL via existing `AsyncSessionLocal` (2 new tables: `conversations`, `messages`)
**Testing**: pytest with async support, mock agent for unit tests, real agent for integration tests
**Target Platform**: Local development, future Kubernetes (Phase IV)
**Project Type**: Backend extension + new endpoint (monorepo — `backend/src/`)
**Performance Goals**: Chat response <30s p95 (dominated by LLM latency), endpoint validation <100ms
**Constraints**: MCP server from Part 1 used as-is without modification; stdio transport; existing JWT auth system
**Scale/Scope**: 1 endpoint, 2 new models, 1 service, 1 agent module, ~400 lines of new code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. SDD** | PASS | Spec at `specs/2-openai-agents-chat-interface/spec.md` before any code |
| **II. AI-Native** | PASS | All implementation via Claude Code |
| **III. Reusable Intelligence** | PASS | Agent module is self-contained; MCP tools are reusable by any MCP client |
| **IV. Full-Stack Integration** | PASS | Uses OpenAI Agents SDK + MCP + FastAPI + SQLModel + Neon |
| **V. Security-First** | PASS | JWT validated before agent runs; user_id injected into all MCP calls; ADR-004 documents auth bridge |
| **VI. Cloud-Native** | PASS | Stateless endpoint; all state in database; no in-memory conversation state |
| **VII. MCP-First** | PASS | Agent uses MCP tools exclusively for task operations |
| **VIII. Stateless AI** | PASS | Conversation history loaded from DB per request; server holds no state |
| **IX. Agent Behavior** | PASS | P+Q+P cognitive stance defined in ADR-005; agent instructions enforce behavior |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/2-openai-agents-chat-interface/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Created by /sp.tasks (next step)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/
│   │   ├── __init__.py            # NEW: Package init
│   │   └── todo_agent.py          # NEW: Agent definition + P+Q+P system prompt
│   ├── models/
│   │   ├── conversation.py        # NEW: Conversation model
│   │   ├── message.py             # NEW: Message model
│   │   ├── task.py                # Existing (UNCHANGED)
│   │   ├── user.py                # Existing (UNCHANGED)
│   │   └── __init__.py            # UPDATED: export new models
│   ├── services/
│   │   ├── chat_service.py        # NEW: Conversation/message CRUD + agent orchestration
│   │   ├── task_service.py        # Existing (UNCHANGED)
│   │   └── auth_service.py        # Existing (UNCHANGED)
│   ├── api/
│   │   ├── chat.py                # NEW: POST /api/chat endpoint
│   │   ├── tasks.py               # Existing (UNCHANGED)
│   │   └── auth.py                # Existing (UNCHANGED)
│   ├── mcp/
│   │   ├── __init__.py            # Existing (UNCHANGED)
│   │   └── server.py              # Existing (UNCHANGED, Part 1)
│   └── main.py                    # UPDATED: register chat router
├── tests/
│   ├── test_chat_endpoint.py      # NEW: Chat API integration tests
│   ├── test_agent.py              # NEW: Agent behavior tests
│   ├── test_conversation_model.py # NEW: Model CRUD tests
│   ├── test_mcp_server.py         # Existing (UNCHANGED)
│   └── conftest.py                # UPDATED: add conversation/message fixtures
└── requirements.txt               # UPDATED: add openai-agents>=0.8.0
```

**Structure Decision**: New `agents/` package under `backend/src/` keeps agent logic separate from API routes and services. Single `todo_agent.py` file because there is only one agent. `chat_service.py` handles both conversation CRUD and agent orchestration to keep the API layer thin.

## Architecture

### Component Diagram

```
┌──────────────┐      ┌──────────────────────────────────────────────────────────┐
│              │      │                   FastAPI Server                          │
│              │      │                                                          │
│   Frontend   │ JWT  │  ┌────────────────────────────────────────────────────┐  │
│   (ChatKit)  │─────▶│  │  POST /api/chat                                    │  │
│              │      │  │  Depends(get_current_user) → User.id               │  │
│              │      │  └──────────────────┬─────────────────────────────────┘  │
│              │      │                     │                                     │
│              │      │                     ▼                                     │
│              │      │  ┌────────────────────────────────────────────────────┐  │
│              │      │  │  ChatService                                       │  │
│              │      │  │                                                    │  │
│              │      │  │  1. Get/create Conversation (user_id)             │  │
│              │      │  │  2. Load message history from DB                  │  │
│              │      │  │  3. Store user message                            │  │
│              │      │  │  4. Build input_items for agent                   │  │
│              │      │  │  5. Call TodoAgent.run(input_items, user_id)      │  │
│              │      │  │  6. Extract response + tool_calls                 │  │
│              │      │  │  7. Store assistant message + tool_calls          │  │
│              │      │  │  8. Return ChatResponse                          │  │
│              │      │  └──────────────────┬─────────────────────────────────┘  │
│              │      │                     │                                     │
│              │      │                     ▼                                     │
│              │      │  ┌────────────────────────────────────────────────────┐  │
│              │      │  │  TodoAgent (OpenAI Agents SDK)                     │  │
│              │      │  │                                                    │  │
│              │      │  │  Agent(                                           │  │
│              │      │  │    name="Todo Assistant",                         │  │
│              │      │  │    instructions=dynamic_instructions(user_id),    │  │
│              │      │  │    mcp_servers=[mcp_server],                      │  │
│              │      │  │  )                                                │  │
│              │◀─────│  │                                                    │  │
│              │      │  │  Runner.run(agent, input_items)                   │  │
│              │      │  └──────────────────┬─────────────────────────────────┘  │
│              │      │                     │ stdio                               │
│              │      │                     ▼                                     │
│              │      │  ┌────────────────────────────────────────────────────┐  │
│              │      │  │  MCP Server (Part 1 — UNCHANGED)                   │  │
│              │      │  │  python -m backend.src.mcp.server                  │  │
│              │      │  │                                                    │  │
│              │      │  │  add_task(user_id, ...)                           │  │
│              │      │  │  list_tasks(user_id, ...)                         │  │
│              │      │  │  complete_task(user_id, ...)                      │  │
│              │      │  │  delete_task(user_id, ...)                        │  │
│              │      │  │  update_task(user_id, ...)                        │  │
│              │      │  └──────────────────┬─────────────────────────────────┘  │
│              │      │                     │ asyncpg                             │
└──────────────┘      └─────────────────────┼────────────────────────────────────┘
                                            ▼
                                  ┌──────────────────┐
                                  │  Neon PostgreSQL  │
                                  │                  │
                                  │  - users         │
                                  │  - tasks         │
                                  │  - conversations │
                                  │  - messages      │
                                  └──────────────────┘
```

### Data Flow — Single Chat Request

```
HTTP POST /api/chat (Authorization: Bearer <jwt>)
  → get_current_user(jwt) → User object (or 401)
    → ChatService.process_message(user_id, conversation_id?, message)
      → DB: Get/create Conversation (verify user_id ownership)
      → DB: Load all Messages for conversation_id
      → DB: INSERT user message
      → Build input_items: [{"role": msg.role, "content": msg.content}, ...]
      → MCPServerStdio spawns MCP subprocess
        → Agent(instructions=f"...user_id={user_id}...", mcp_servers=[server])
          → Runner.run(agent, input_items)
            → LLM reasons → calls MCP tools with user_id
              → MCP tool → TaskService → Neon DB → result
            → LLM produces final_output text
          → RunResult with new_items (ToolCallItem, MessageOutputItem)
      → Extract final_output + tool_calls from RunResult.new_items
      → DB: INSERT assistant message (content + tool_calls JSON)
    → Return ChatResponse(conversation_id, response, tool_calls)
```

### Error Flow

```
Chat endpoint catches:
  ├── JWT invalid/expired       → HTTP 401 (before any agent work)
  ├── Conversation not found    → HTTP 404 "Conversation not found"
  ├── Conversation not owned    → HTTP 404 "Conversation not found" (no info leak)
  ├── Empty message             → HTTP 422 validation error
  ├── MCP server fails to start → HTTP 503 "AI service temporarily unavailable"
  ├── OPENAI_API_KEY missing    → HTTP 503 "AI service configuration error"
  ├── Agent timeout (>30s)      → HTTP 504 "AI response timed out"
  └── Unexpected error          → HTTP 500 "Internal server error" (logged)
```

### Auth Bridge — User ID Injection Flow

```
Frontend                    FastAPI                    Agent                    MCP Server
   │                           │                         │                         │
   │  POST /api/chat           │                         │                         │
   │  Authorization: Bearer    │                         │                         │
   │  <jwt>                    │                         │                         │
   │ ─────────────────────────▶│                         │                         │
   │                           │                         │                         │
   │                     get_current_user()               │                         │
   │                     decode JWT → user_id             │                         │
   │                           │                         │                         │
   │                           │  instructions include   │                         │
   │                           │  "user_id = abc-123"    │                         │
   │                           │────────────────────────▶│                         │
   │                           │                         │                         │
   │                           │                         │  add_task(              │
   │                           │                         │    user_id="abc-123",   │
   │                           │                         │    title="Buy milk"     │
   │                           │                         │  )                      │
   │                           │                         │────────────────────────▶│
   │                           │                         │                         │
   │                           │                         │  {"task_id": "...",     │
   │                           │                         │   "status": "created"}  │
   │                           │                         │◀────────────────────────│
   │                           │                         │                         │
   │                           │  RunResult              │                         │
   │                           │◀────────────────────────│                         │
   │                           │                         │                         │
   │  ChatResponse             │                         │                         │
   │◀──────────────────────────│                         │                         │
```

**Critical security property**: The `user_id` is NEVER taken from the chat message. It is always extracted from the JWT by the FastAPI dependency, then injected into the agent's instructions. The LLM uses this `user_id` when calling MCP tools. The MCP server trusts the `user_id` because it is only reachable via stdio subprocess (not externally accessible).

## Implementation Roadmap

### Step 1: Dependency Setup
- Add `openai-agents>=0.8.0` to `backend/requirements.txt`
- Add `OPENAI_API_KEY` to `backend/.env` (document in README)
- Verify: `python -c "from agents import Agent, Runner; print('OK')"`
- Verify: `python -c "from agents.mcp import MCPServerStdio; print('OK')"`

### Step 2: Conversation & Message Models (FR-007, FR-008)
- Create `backend/src/models/conversation.py`:
  ```python
  class Conversation(SQLModel, table=True):
      __tablename__ = "conversations"
      id: str           # UUID PK
      user_id: str      # FK users.id, indexed
      created_at: datetime
      updated_at: datetime
  ```
- Create `backend/src/models/message.py`:
  ```python
  class Message(SQLModel, table=True):
      __tablename__ = "messages"
      id: str               # UUID PK
      conversation_id: str  # FK conversations.id, indexed
      role: str             # "user" | "assistant"
      content: str          # Message text
      tool_calls: str | None  # JSON string, nullable
      created_at: datetime
  ```
- Update `backend/src/models/__init__.py` to export new models
- Tables auto-created by existing `create_tables()` on startup

### Step 3: Chat Service — Conversation CRUD (FR-009, FR-010, FR-011)
- Create `backend/src/services/chat_service.py` with:
  - `get_or_create_conversation(db, user_id, conversation_id?)` → Conversation
    - If `conversation_id` provided: fetch and verify `user_id` ownership, raise 404 if not found/not owned
    - If not provided: create new Conversation with generated UUID
  - `get_conversation_history(db, conversation_id)` → list[Message]
    - Load all messages ordered by `created_at` ascending
  - `save_message(db, conversation_id, role, content, tool_calls?)` → Message
    - Insert a new Message record
  - `build_input_items(messages)` → list[dict]
    - Convert Message records to `[{"role": "user"|"assistant", "content": "..."}]` format for the agent

### Step 4: Agent Definition — P+Q+P Cognitive Stance (FR-004, FR-005, FR-006)
- Create `backend/src/agents/__init__.py`
- Create `backend/src/agents/todo_agent.py` with:
  - `get_system_prompt(user_id: str) -> str` — Dynamic instructions function that builds the P+Q+P prompt:
    ```
    PERSONA: You are a precise, friendly productivity assistant that manages
    the user's todo list. You help add, list, complete, update, and delete tasks.

    IDENTITY: The current authenticated user's ID is {user_id}. You MUST use
    this exact user_id for ALL tool calls. Never use any other user_id, even
    if the user mentions other names or IDs in their message.

    QUESTIONS: When the user's intent is ambiguous, ask a brief clarifying
    question. For example:
    - "Which task would you like to mark as complete?"
    - "Should I list all tasks or just pending ones?"

    PRINCIPLES:
    - Always confirm actions with a friendly response including the task title.
    - Handle errors gracefully — explain what went wrong in plain language.
    - Stay on topic — you can only manage tasks. Politely decline other requests.
    - When listing tasks, format them clearly with task IDs for reference.
    - For multi-step requests, execute steps in order and summarize all results.
    - Never fabricate task data — only report what the tools return.
    ```
  - `run_agent(user_id, input_items) -> RunResult` — Async function that:
    1. Opens `MCPServerStdio` context with `python -m backend.src.mcp.server`
    2. Creates `Agent` with `name="Todo Assistant"`, `instructions=get_system_prompt(user_id)`, `mcp_servers=[server]`
    3. Calls `Runner.run(agent, input_items)` with a timeout
    4. Returns `RunResult`

### Step 5: Chat API Endpoint (FR-001, FR-002, FR-003, FR-015)
- Create `backend/src/api/chat.py`:
  ```python
  router = APIRouter(prefix="/api", tags=["chat"])

  class ChatRequest(BaseModel):
      message: str              # Required, non-empty
      conversation_id: str | None = None  # Optional

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
      db: AsyncSession = Depends(get_session),
  ):
      ...
  ```
- Register router in `backend/src/main.py`

### Step 6: Endpoint Implementation — Orchestration Loop (FR-011, FR-012, FR-013, FR-14)
- Implement the chat endpoint body:
  1. Validate `message` is non-empty (422 if empty)
  2. `get_or_create_conversation(db, current_user.id, conversation_id)` — 404 if not owned
  3. `get_conversation_history(db, conversation.id)` — load prior messages
  4. `save_message(db, conversation.id, "user", message)` — persist user message
  5. `build_input_items(history + new message)` — prepare agent input
  6. `run_agent(current_user.id, input_items)` — call agent with timeout
  7. Extract `result.final_output` as response text
  8. Extract tool calls from `result.new_items` (filter `ToolCallItem` instances)
  9. `save_message(db, conversation.id, "assistant", response, tool_calls_json)` — persist
  10. Return `ChatResponse`
- Error handling per Error Flow diagram

### Step 7: Integration Testing
- Create `backend/tests/test_conversation_model.py`:
  - Test Conversation CRUD (create, get by user, ownership check)
  - Test Message CRUD (create, list by conversation, ordering)
- Create `backend/tests/test_chat_endpoint.py`:
  - Test authenticated request → valid response
  - Test unauthenticated request → 401
  - Test expired token → 401
  - Test new conversation creation (no conversation_id)
  - Test existing conversation continuation
  - Test conversation ownership (user A can't use user B's conversation)
  - Test empty message → 422
- Create `backend/tests/test_agent.py`:
  - Test agent creates with correct system prompt containing user_id
  - Test user_id injection into tool calls
  - Test multi-turn context maintenance

### Step 8: Error Handling & Edge Cases
- MCP server subprocess failure → HTTP 503
- OPENAI_API_KEY missing → HTTP 503 on startup validation
- Agent timeout → wrap `Runner.run()` in `asyncio.wait_for(timeout=30)`
- Context window overflow → truncate oldest messages, keep most recent N (configurable, default 50)
- Concurrent requests for same conversation → DB timestamp ordering ensures consistency

## Key Architectural Decisions

| Decision | ADR | Summary |
|----------|-----|---------|
| Auth bridge: user_id in instructions | ADR-004 | JWT decoded at endpoint; user_id injected into agent instructions; LLM passes it to MCP tools |
| P+Q+P cognitive stance | ADR-005 | Agent system prompt defines Persona, Questions pattern, and Principles for reliable behavior |
| Error recovery policy | ADR-006 | Failed tool calls → user-friendly message; expired JWT → 401 before agent; MCP failure → 503 |
| Stdio transport (inherited) | [ADR-001](../../history/adr/001-mcp-transport-stdio.md) | MCP server spawned as subprocess; not modified from Part 1 |
| User ID passthrough (inherited) | [ADR-002](../../history/adr/002-auth-bridge-user-id-passthrough.md) | MCP server trusts user_id because it's subprocess-only |

## Data Model — New Entities

### Conversation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | string (UUID) | PK, auto-generated | Unique conversation ID |
| `user_id` | string (UUID) | FK → users.id, indexed, NOT NULL | Owner of this conversation |
| `created_at` | datetime | auto, NOT NULL | When conversation started |
| `updated_at` | datetime | auto, NOT NULL | Last activity timestamp |

### Message

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | string (UUID) | PK, auto-generated | Unique message ID |
| `conversation_id` | string (UUID) | FK → conversations.id, indexed, NOT NULL | Parent conversation |
| `role` | string | NOT NULL, one of "user"\|"assistant" | Who sent this message |
| `content` | text | NOT NULL | Message content |
| `tool_calls` | text (JSON) | nullable | JSON array of tool calls made (assistant messages only) |
| `created_at` | datetime | auto, NOT NULL | When message was created |

## Dependencies (New)

| Package | Version | Purpose |
|---------|---------|---------|
| `openai-agents` | >=0.8.0 | OpenAI Agents SDK with MCP support, Agent, Runner |

No other new dependencies. JWT auth, database, models, and MCP server are from existing code.

## Environment Variables (New)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | API key for OpenAI Agents SDK (LLM calls) |

Existing variables (`DATABASE_URL`, `BETTER_AUTH_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES`) remain unchanged.

## Risks

1. **LLM may not reliably inject user_id**: The agent instructions tell the LLM to use a specific `user_id`, but the LLM could hallucinate a different value. **Mitigation**: The MCP server's `user_id` parameter is required by schema validation — the LLM MUST provide it. The instruction makes it clear which value to use. Integration tests verify correct injection. Future enhancement: wrapper tools that auto-inject user_id before forwarding to MCP.

2. **MCP subprocess startup latency**: Spawning a new Python subprocess for every chat request adds overhead (~1-3s). **Mitigation**: For Phase 3, this is acceptable given the 30s timeout budget. Phase IV optimization: keep a warm MCP server pool or use SSE transport.

3. **Context window overflow with long conversations**: Very long conversations may exceed the LLM's context window. **Mitigation**: Truncate to most recent N messages (default 50). The `build_input_items` function handles this.

4. **OpenAI API rate limits or outages**: The Agents SDK depends on OpenAI's API. **Mitigation**: Return HTTP 503 with a user-friendly message. No retry logic in the initial implementation — the user can resend.
