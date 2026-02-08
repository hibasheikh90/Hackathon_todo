# Feature Specification: Phase 3 Part 2 — OpenAI Agents SDK and Auth Integration

**Feature Branch**: `2-openai-agents-chat-interface`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase 3 Part 2: OpenAI Agents SDK and Auth Integration — Implement the core AI Agent logic to orchestrate user requests and securely interface with the Phase 2 backend using the MCP tools developed in Part 1."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — User Sends a Chat Message and Gets an AI Response (Priority: P1)

A logged-in user sends a natural language message through the chat endpoint (e.g., "Show me all my tasks"). The backend extracts the user's identity from their JWT token, creates or retrieves a conversation, feeds the message history plus the new message to the OpenAI Agents SDK agent, and returns the agent's response along with any MCP tool calls that were invoked.

**Why this priority**: This is the core request-response cycle. Without it, no other chat functionality exists. It validates the entire pipeline: JWT → Agent → MCP → Database → Response.

**Independent Test**: Can be tested by sending a POST request with a valid JWT and a message, verifying the response contains a conversation_id, an assistant response string, and the correct tool_calls array.

**Acceptance Scenarios**:

1. **Given** a logged-in user with valid JWT, **When** `POST /api/chat` is called with `{"message": "Show me all my tasks"}`, **Then** the agent invokes `list_tasks` via MCP with the authenticated user's ID, and the response contains `{"conversation_id": "<uuid>", "response": "<natural language listing>", "tool_calls": [{"tool": "list_tasks", ...}]}`.
2. **Given** a logged-in user with valid JWT, **When** `POST /api/chat` is called with `{"message": "Add a task to buy groceries"}`, **Then** the agent invokes `add_task` via MCP, and the response confirms the task was created with the task title.
3. **Given** a request with no Authorization header, **When** `POST /api/chat` is called, **Then** the endpoint returns HTTP 401 with `{"detail": "Not authenticated"}`.
4. **Given** a request with an expired JWT, **When** `POST /api/chat` is called, **Then** the endpoint returns HTTP 401 with `{"detail": "Token has expired"}`.

---

### User Story 2 — Agent Maintains Conversation Context Within a Session (Priority: P1)

A user sends multiple messages within the same conversation. The agent uses stored message history to maintain context across turns. For example, after listing tasks, the user says "Mark the first one as complete" — the agent uses prior context to determine which task is "the first one."

**Why this priority**: Without short-term memory, the agent cannot handle multi-turn interactions, which is the core value proposition of a chat interface over a simple API.

**Independent Test**: Can be tested by sending a sequence of messages within the same conversation_id and verifying the agent correctly resolves references to prior context.

**Acceptance Scenarios**:

1. **Given** a user starts a new conversation (no conversation_id), **When** the first message is sent, **Then** a new Conversation record is created in the database and the conversation_id is returned.
2. **Given** a user has an existing conversation with prior messages, **When** a new message is sent with the same `conversation_id`, **Then** the agent receives the full prior message history and can reference previous context.
3. **Given** a user says "Show me my tasks" and then "Mark the first one as complete", **When** the second message is sent with the same conversation_id, **Then** the agent uses the prior `list_tasks` result to identify the correct task and calls `complete_task` with the right `task_id`.
4. **Given** a user provides an invalid `conversation_id` that does not belong to them, **When** a message is sent, **Then** the endpoint returns HTTP 404 with `{"detail": "Conversation not found"}`.

---

### User Story 3 — Authentication Bridge Injects User Identity into MCP Tool Calls (Priority: P1)

The chat endpoint extracts the `user_id` from the JWT token and injects it into every MCP tool call made by the agent. The user never provides their own `user_id` — it is always derived from the authenticated session. This prevents one user from manipulating another user's tasks.

**Why this priority**: Security is non-negotiable. The auth bridge is the critical link between the frontend authentication layer and the MCP tools that enforce user isolation.

**Independent Test**: Can be tested by verifying that when the agent calls any MCP tool, the `user_id` parameter matches the JWT subject claim, regardless of what the user says in their message.

**Acceptance Scenarios**:

1. **Given** user "alice" is authenticated, **When** she says "Add a task for bob to buy milk", **Then** the agent creates the task under alice's `user_id` (from JWT), NOT bob's, and the response confirms the task was added for the current user.
2. **Given** user "alice" is authenticated, **When** the agent calls `list_tasks`, **Then** the `user_id` parameter passed to the MCP tool is always alice's ID extracted from the JWT — never a value from the chat message.
3. **Given** user "alice" is authenticated, **When** the agent calls `delete_task`, **Then** the `user_id` injected into the MCP call matches alice's JWT subject, ensuring she can only delete her own tasks.

---

### User Story 4 — Agent Uses P+Q+P Cognitive Stance (Priority: P2)

The agent operates as a precise, task-oriented productivity assistant. It follows a defined behavioral pattern: it has a clear **Persona** (helpful productivity assistant), asks clarifying **Questions** when intent is ambiguous, and follows strict **Principles** (confirm actions, handle errors gracefully, never fabricate task data).

**Why this priority**: Agent behavior quality is important for user experience but the system is functional without it. It can be refined iteratively after the core pipeline works.

**Independent Test**: Can be tested by sending ambiguous or edge-case messages and verifying the agent responds according to the behavioral spec.

**Acceptance Scenarios**:

1. **Given** the agent receives "Do my stuff", **When** the intent is ambiguous, **Then** the agent asks a clarifying question rather than guessing which tool to invoke.
2. **Given** the agent successfully adds a task, **When** responding to the user, **Then** the response includes a friendly confirmation with the task title (e.g., "I've added 'Buy groceries' to your task list.").
3. **Given** an MCP tool returns an error (e.g., task not found), **When** the agent processes the error, **Then** it provides a user-friendly explanation rather than exposing raw error details.
4. **Given** the agent is asked something outside its scope (e.g., "What's the weather?"), **Then** it politely declines and reminds the user it can help with task management.

---

### User Story 5 — Agent Handles Multi-Step Intents (Priority: P2)

A user issues a complex request that requires multiple MCP tool calls in sequence. For example, "Find my pending tasks and mark the one about groceries as complete." The agent reasons through the steps: first list pending tasks, then identify the correct task, then complete it.

**Why this priority**: Multi-step reasoning is a key differentiator of an agent over simple tool dispatch. It depends on the core pipeline (P1) working first.

**Independent Test**: Can be tested by sending a multi-step request and verifying the agent correctly chains multiple tool calls and returns a coherent response.

**Acceptance Scenarios**:

1. **Given** user has tasks including "Buy groceries" (pending), **When** user says "Find my pending tasks and mark the groceries one as complete", **Then** the agent calls `list_tasks(status="pending")` first, identifies the groceries task, then calls `complete_task(task_id=<correct_id>)`, and returns a confirmation.
2. **Given** user says "Delete all my completed tasks", **When** the agent processes this, **Then** it calls `list_tasks(status="completed")` first, then calls `delete_task` for each completed task, and returns a summary of what was deleted.
3. **Given** user says "Add three tasks: buy milk, call mom, and clean the house", **When** the agent processes this, **Then** it calls `add_task` three times with the correct titles and returns a confirmation listing all three.

---

### User Story 6 — Conversation Persistence Across Server Restarts (Priority: P2)

A user can resume a previous conversation after the server restarts. Since the server is stateless, all conversation state is stored in the database. When a request arrives with a `conversation_id`, the server fetches the full message history from the database and provides it to the agent.

**Why this priority**: Persistence is important for production readiness but the chat is functional within a single session without it (new conversations work regardless).

**Independent Test**: Can be tested by creating a conversation, restarting the server (or using a fresh session), and sending a message with the same conversation_id — verifying the agent has access to prior context.

**Acceptance Scenarios**:

1. **Given** a conversation with ID "conv-123" and 5 prior messages in the database, **When** the server is restarted and a new message is sent with `conversation_id: "conv-123"`, **Then** the agent receives all 5 prior messages as context and responds coherently.
2. **Given** a user has multiple conversations, **When** they send a message with a specific `conversation_id`, **Then** only the messages from that conversation are loaded (not messages from other conversations).

---

### Edge Cases

- What happens when the MCP server subprocess fails to start? The chat endpoint MUST return HTTP 503 with a clear error message ("AI service temporarily unavailable") rather than hanging or crashing.
- What happens when the OpenAI Agents SDK API key is missing or invalid? The chat endpoint MUST return HTTP 503 with "AI service configuration error."
- What happens when a conversation has more messages than the agent's context window can handle? The system MUST truncate oldest messages while preserving the most recent N messages (configurable).
- What happens when the agent takes too long to respond? The chat endpoint MUST enforce a timeout (30 seconds default) and return HTTP 504 if exceeded.
- What happens when two concurrent requests arrive for the same conversation? The database MUST enforce message ordering via timestamps, and each request MUST fetch the latest state before processing.
- What happens when the user sends an empty message? The endpoint MUST return HTTP 422 with a validation error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a chat endpoint `POST /api/chat` that accepts a JWT-authenticated request with `message` (string, required) and `conversation_id` (string, optional).
- **FR-002**: The chat endpoint MUST extract the `user_id` from the JWT token using the existing `get_current_user` dependency from `backend/src/dependencies/auth.py`.
- **FR-003**: The chat endpoint MUST return a JSON response with `conversation_id` (string), `response` (string), and `tool_calls` (array of objects with `tool` name and `arguments`).
- **FR-004**: System MUST implement an OpenAI Agents SDK agent that uses the Phase 3 Part 1 MCP server as its tool provider via stdio transport.
- **FR-005**: The agent MUST receive the authenticated `user_id` as a parameter and inject it into every MCP tool call automatically. The user MUST NOT be able to override this via chat messages.
- **FR-006**: The agent MUST be configured with a system prompt defining the P+Q+P cognitive stance: Persona (productivity assistant), Questions (ask when ambiguous), Principles (confirm actions, handle errors gracefully, stay on-topic).
- **FR-007**: System MUST implement a `Conversation` database model with fields: `id` (UUID, PK), `user_id` (string, FK to users), `created_at` (datetime), `updated_at` (datetime).
- **FR-008**: System MUST implement a `Message` database model with fields: `id` (UUID, PK), `conversation_id` (string, FK to conversations), `role` (string: "user" or "assistant"), `content` (text), `tool_calls` (JSON, nullable), `created_at` (datetime).
- **FR-009**: When no `conversation_id` is provided, the endpoint MUST create a new Conversation and return its ID.
- **FR-010**: When a `conversation_id` is provided, the endpoint MUST verify it belongs to the authenticated user before loading message history. Return HTTP 404 if not found or not owned.
- **FR-011**: The endpoint MUST store the user's message in the database BEFORE running the agent, and store the agent's response AFTER the agent completes.
- **FR-012**: The endpoint MUST pass the full conversation history (all prior messages for the conversation) to the agent as context.
- **FR-013**: The MCP server MUST be spawned as a stdio subprocess by the agent, reusing the existing `backend/src/mcp/server.py` from Part 1 without modification.
- **FR-014**: Error responses from the agent or MCP tools MUST be surfaced as user-friendly messages in the `response` field, never as raw stack traces or internal errors.
- **FR-015**: The chat endpoint MUST enforce rate limiting consistent with existing API patterns (e.g., 20 requests/minute).

### Key Entities

- **Conversation** (new): `id` (string/UUID, PK), `user_id` (string, FK to users.id, indexed), `created_at` (datetime, auto), `updated_at` (datetime, auto). Defined in `backend/src/models/conversation.py`.
- **Message** (new): `id` (string/UUID, PK), `conversation_id` (string, FK to conversations.id, indexed), `role` (string, one of "user"|"assistant"), `content` (text), `tool_calls` (JSON, nullable), `created_at` (datetime, auto). Defined in `backend/src/models/message.py`.
- **User** (existing, unchanged): `id`, `email`, `password_hash`, `is_active`, `created_at`, `updated_at`. Defined in `backend/src/models/user.py`.
- **Task** (existing, unchanged): `id`, `title`, `description`, `is_completed`, `user_id`, `created_at`, `updated_at`. Defined in `backend/src/models/task.py`.

### Integration Points

- **Authentication Layer**: The chat endpoint MUST use `Depends(get_current_user)` from `backend/src/dependencies/auth.py` to extract the authenticated user.
- **MCP Server (Part 1)**: The OpenAI Agents SDK MUST connect to `backend/src/mcp/server.py` via stdio transport. The MCP server is used as-is without modification.
- **Database Layer**: New models MUST use `AsyncSessionLocal` from `backend/src/database/__init__.py` for session management, following the same async patterns as existing code.
- **OpenAI Agents SDK**: The agent MUST be created using `openai-agents` package with MCP server integration via `MCPServerStdio`.
- **Environment**: The system MUST read `OPENAI_API_KEY` from environment variables for the Agents SDK. The existing `DATABASE_URL` and `BETTER_AUTH_SECRET` continue to be used.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chat endpoint responds to valid authenticated requests within 30 seconds (p95 latency, accounting for LLM response time).
- **SC-002**: The agent correctly extracts user_id from JWT and injects it into 100% of MCP tool calls — verified by test.
- **SC-003**: Unauthenticated requests (no JWT, expired JWT, invalid JWT) are rejected with HTTP 401 before any agent processing occurs.
- **SC-004**: Multi-turn conversations maintain context — a follow-up message can reference results from a prior turn within the same conversation.
- **SC-005**: Conversation and message records are persisted correctly in the database after each interaction.
- **SC-006**: The agent can successfully chain multiple MCP tool calls in a single response for multi-step intents.
- **SC-007**: The MCP server subprocess starts and connects successfully when the chat endpoint is invoked.
- **SC-008**: Error cases (MCP failure, timeout, invalid input) return appropriate HTTP status codes and user-friendly error messages.

### File Structure (Expected Output)

```
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py        # NEW: Conversation model
│   │   ├── message.py             # NEW: Message model
│   │   ├── task.py                # Existing (unchanged)
│   │   ├── user.py                # Existing (unchanged)
│   │   └── __init__.py            # Updated: export new models
│   ├── services/
│   │   ├── chat_service.py        # NEW: Conversation/message CRUD + agent orchestration
│   │   ├── task_service.py        # Existing (unchanged)
│   │   └── auth_service.py        # Existing (unchanged)
│   ├── api/
│   │   ├── chat.py                # NEW: POST /api/chat endpoint
│   │   ├── tasks.py               # Existing (unchanged)
│   │   └── auth.py                # Existing (unchanged)
│   ├── agent/
│   │   ├── __init__.py            # NEW: Agent package (named 'agent' to avoid shadowing openai-agents)
│   │   └── todo_agent.py          # NEW: OpenAI Agents SDK agent definition + P+Q+P prompt
│   ├── mcp/
│   │   ├── __init__.py            # Existing (unchanged)
│   │   └── server.py              # Existing (unchanged, Part 1)
│   ├── main.py                    # Updated: register chat router
│   └── ...
├── tests/
│   ├── test_chat_endpoint.py      # NEW: Chat API integration tests
│   ├── test_agent.py              # NEW: Agent behavior unit tests
│   ├── test_conversation_model.py # NEW: Model tests
│   ├── test_mcp_server.py         # Existing (unchanged)
│   └── conftest.py                # Updated: add conversation/message fixtures
└── requirements.txt               # Updated: add openai-agents
```
