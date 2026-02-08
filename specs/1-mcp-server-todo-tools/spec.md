# Feature Specification: Phase 3 Part 1 — MCP Server and Tooling

**Feature Branch**: `1-mcp-server-todo-tools`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Phase 3 Part 1: MCP Server and Tooling — Develop an Official MCP SDK server that exposes Phase 2 FastAPI backend functionality to the AI agent."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — AI Agent Creates a Task via MCP (Priority: P1)

An AI agent (powered by OpenAI Agents SDK) receives a natural language request like "Add a task to buy groceries." The agent invokes the `add_task` MCP tool with the user's ID, title, and optional description. The MCP server communicates with the Neon PostgreSQL database through the existing service layer, creates the task, and returns a structured confirmation.

**Why this priority**: Task creation is the most fundamental operation. Without it, no other tool has data to operate on. This validates the entire MCP → Service Layer → Database pipeline end-to-end.

**Independent Test**: Can be fully tested by invoking the `add_task` tool with valid parameters and verifying the task appears in the database with correct `user_id`, `title`, and `description`. Delivers immediate value as the agent can begin managing tasks.

**Acceptance Scenarios**:

1. **Given** the MCP server is running and connected to the database, **When** the `add_task` tool is called with `{"user_id": "abc-123", "title": "Buy groceries", "description": "Milk, eggs, bread"}`, **Then** a new task is created in the `tasks` table with `user_id = "abc-123"`, the response contains `{"task_id": "<uuid>", "status": "created", "title": "Buy groceries"}`.
2. **Given** the MCP server is running, **When** `add_task` is called with `{"user_id": "abc-123", "title": "Quick note"}` (no description), **Then** the task is created with `description = null` and the response confirms creation.
3. **Given** the MCP server is running, **When** `add_task` is called with `{"user_id": "abc-123", "title": ""}` (empty title), **Then** the tool returns an error response with a clear message indicating title is required.

---

### User Story 2 — AI Agent Lists Tasks via MCP (Priority: P1)

An AI agent receives a request like "Show me all my tasks" or "What's pending?" The agent invokes the `list_tasks` MCP tool with the user's ID and an optional status filter. The MCP server queries the database and returns an array of task objects.

**Why this priority**: Listing tasks is equally fundamental — the agent needs to see existing tasks to perform completions, updates, and deletions by reference. Tied P1 with creation.

**Independent Test**: Can be tested by creating tasks in the database for a user, then calling `list_tasks` and verifying the returned array matches. Delivers value as the agent can report task status.

**Acceptance Scenarios**:

1. **Given** user "abc-123" has 3 tasks (2 pending, 1 completed), **When** `list_tasks` is called with `{"user_id": "abc-123", "status": "all"}`, **Then** the response contains an array of 3 task objects each with `id`, `title`, `description`, `is_completed`, `created_at`.
2. **Given** user "abc-123" has tasks, **When** `list_tasks` is called with `{"user_id": "abc-123", "status": "pending"}`, **Then** only tasks where `is_completed = false` are returned.
3. **Given** user "abc-123" has tasks, **When** `list_tasks` is called with `{"user_id": "abc-123", "status": "completed"}`, **Then** only tasks where `is_completed = true` are returned.
4. **Given** user "abc-123" has no tasks, **When** `list_tasks` is called, **Then** the response contains an empty array `[]`.

---

### User Story 3 — AI Agent Marks a Task Complete via MCP (Priority: P2)

An AI agent receives "Mark task 3 as done" or "I finished buying groceries." The agent invokes the `complete_task` MCP tool with the user's ID and task ID. The MCP server toggles the task's `is_completed` status and returns confirmation.

**Why this priority**: Completing tasks is the core value loop of a todo app. It depends on tasks existing (P1) but is the primary action users take.

**Independent Test**: Can be tested by creating a pending task, calling `complete_task`, and verifying `is_completed` flipped to `true` in the database. Also test toggling back to `false`.

**Acceptance Scenarios**:

1. **Given** user "abc-123" has a pending task with `id = "task-uuid-1"`, **When** `complete_task` is called with `{"user_id": "abc-123", "task_id": "task-uuid-1"}`, **Then** the task's `is_completed` becomes `true` and the response is `{"task_id": "task-uuid-1", "status": "completed", "title": "Buy groceries"}`.
2. **Given** user "abc-123" has a completed task with `id = "task-uuid-1"`, **When** `complete_task` is called again, **Then** the task's `is_completed` toggles back to `false` and the response status reflects the new state.
3. **Given** user "abc-123" calls `complete_task` with a `task_id` that does not exist or belongs to another user, **Then** the tool returns an error response: `{"error": "Task not found or access denied"}`.

---

### User Story 4 — AI Agent Updates a Task via MCP (Priority: P2)

An AI agent receives "Change task 1 title to 'Buy groceries and fruits'" or "Update the description of my meeting task." The agent invokes the `update_task` MCP tool with the user's ID, task ID, and the fields to update.

**Why this priority**: Updating tasks is a common action but less frequent than creation or completion. Depends on tasks existing.

**Independent Test**: Can be tested by creating a task, calling `update_task` with new title/description, and verifying the database reflects the changes.

**Acceptance Scenarios**:

1. **Given** user "abc-123" has a task `id = "task-uuid-1"` with title "Buy groceries", **When** `update_task` is called with `{"user_id": "abc-123", "task_id": "task-uuid-1", "title": "Buy groceries and fruits"}`, **Then** the task title is updated and the response is `{"task_id": "task-uuid-1", "status": "updated", "title": "Buy groceries and fruits"}`.
2. **Given** the same task, **When** `update_task` is called with only `{"user_id": "abc-123", "task_id": "task-uuid-1", "description": "Get organic produce"}`, **Then** only the description is updated; the title remains unchanged.
3. **Given** user "abc-123" calls `update_task` with a `task_id` belonging to another user, **Then** the tool returns an error: `{"error": "Task not found or access denied"}`.

---

### User Story 5 — AI Agent Deletes a Task via MCP (Priority: P2)

An AI agent receives "Delete the old task" or "Remove task 2." The agent invokes the `delete_task` MCP tool with the user's ID and task ID. The task is permanently removed from the database.

**Why this priority**: Deletion is important but destructive. Ranked after update since it's less frequently used.

**Independent Test**: Can be tested by creating a task, calling `delete_task`, and verifying the task no longer exists in the database.

**Acceptance Scenarios**:

1. **Given** user "abc-123" has a task `id = "task-uuid-1"`, **When** `delete_task` is called with `{"user_id": "abc-123", "task_id": "task-uuid-1"}`, **Then** the task is removed from the database and the response is `{"task_id": "task-uuid-1", "status": "deleted", "title": "Buy groceries"}`.
2. **Given** user "abc-123" calls `delete_task` with a non-existent `task_id`, **Then** the tool returns an error: `{"error": "Task not found or access denied"}`.
3. **Given** user "abc-123" calls `delete_task` with a `task_id` belonging to user "xyz-456", **Then** the tool returns an error: `{"error": "Task not found or access denied"}`.

---

### User Story 6 — MCP Server Startup and Tool Discovery (Priority: P1)

A developer or AI framework connects to the MCP server. The server exposes its available tools with full metadata (names, descriptions, parameter schemas). The connecting client can introspect all 5 tools before invoking any of them.

**Why this priority**: Without server startup and tool discovery, no tool can be called. This is the foundational infrastructure story.

**Independent Test**: Can be tested by starting the MCP server and calling the MCP `list_tools` / `tools/list` method, verifying all 5 tools are returned with correct schemas.

**Acceptance Scenarios**:

1. **Given** the MCP server binary/script is executed, **When** startup completes, **Then** the server is listening for MCP protocol connections within 30 seconds.
2. **Given** the MCP server is running, **When** a client sends a `tools/list` request, **Then** the response contains exactly 5 tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`, each with `name`, `description`, and `inputSchema` fields.
3. **Given** each tool's `inputSchema`, **Then** `user_id` is marked as required in every tool, `title` is required for `add_task`, `task_id` is required for `complete_task`, `delete_task`, and `update_task`.

---

### Edge Cases

- What happens when the database connection is unavailable at MCP server startup? The server MUST log a clear error and fail fast rather than silently operating without a database.
- What happens when a tool is called with a `user_id` that does not exist in the `users` table? The tool MUST still operate (tasks are keyed by `user_id` string, no FK enforcement needed at MCP level — the service layer handles this).
- What happens when `update_task` is called with no fields to update (only `user_id` and `task_id`)? The tool MUST return the current task state without modification (no-op update).
- What happens when `list_tasks` is called with an invalid `status` value (e.g., "archived")? The tool MUST return an error indicating valid status values are "all", "pending", or "completed".
- What happens when tool parameters have incorrect types (e.g., `task_id` as an integer instead of string)? The MCP SDK schema validation MUST reject the call with a clear validation error.
- What happens when two concurrent `complete_task` calls toggle the same task? The database's transactional isolation MUST ensure consistent state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement an MCP server using the Official MCP SDK for Python (`mcp` package).
- **FR-002**: The MCP server MUST expose exactly 5 tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`.
- **FR-003**: The `add_task` tool MUST accept parameters: `user_id` (string, required), `title` (string, required), `description` (string, optional). It MUST return `{"task_id": "<uuid>", "status": "created", "title": "<title>"}`.
- **FR-004**: The `list_tasks` tool MUST accept parameters: `user_id` (string, required), `status` (string, optional — one of "all", "pending", "completed", defaults to "all"). It MUST return an array of task objects with fields: `id`, `title`, `description`, `is_completed`, `created_at`.
- **FR-005**: The `complete_task` tool MUST accept parameters: `user_id` (string, required), `task_id` (string, required). It MUST toggle the task's `is_completed` field and return `{"task_id": "<id>", "status": "completed"|"pending", "title": "<title>"}`.
- **FR-006**: The `delete_task` tool MUST accept parameters: `user_id` (string, required), `task_id` (string, required). It MUST remove the task and return `{"task_id": "<id>", "status": "deleted", "title": "<title>"}`.
- **FR-007**: The `update_task` tool MUST accept parameters: `user_id` (string, required), `task_id` (string, required), `title` (string, optional), `description` (string, optional). It MUST update only the provided fields and return `{"task_id": "<id>", "status": "updated", "title": "<title>"}`.
- **FR-008**: Every tool MUST enforce user isolation — a user can only access tasks where `task.user_id` matches the provided `user_id`.
- **FR-009**: The MCP server MUST reuse the existing database infrastructure from Phase 2 (`backend/src/database/`, `backend/src/models/`, `backend/src/services/task_service.py`) rather than duplicating database logic.
- **FR-010**: Each tool MUST include a human-readable `description` in its MCP tool definition that clearly explains what the tool does, suitable for AI agent introspection.
- **FR-011**: Each tool MUST define an `inputSchema` (JSON Schema) that specifies required and optional parameters with types and descriptions.
- **FR-012**: Error responses from tools MUST be returned as structured content (not exceptions) with clear error messages the AI agent can relay to the user.
- **FR-013**: The MCP server MUST support the stdio transport for local development and testing (compatible with Claude Desktop, MCP Inspector, and OpenAI Agents SDK MCP integration).

### Key Entities

- **Task** (existing): `id` (string/UUID), `title` (string, 1-255 chars), `description` (string, optional, up to 10000 chars), `is_completed` (boolean), `user_id` (string/UUID FK), `created_at` (datetime), `updated_at` (datetime). Defined in `backend/src/models/task.py`.
- **User** (existing): `id` (string/UUID), `email` (string), `password_hash` (string), `is_active` (boolean), `created_at` (datetime), `updated_at` (datetime). Defined in `backend/src/models/user.py`.
- **MCP Tool Definition**: `name` (string), `description` (string), `inputSchema` (JSON Schema object). Defined by the Official MCP SDK protocol.

### Integration Points

- **Database Layer**: The MCP server MUST import and use `AsyncSessionLocal` from `backend/src/database/__init__.py` to obtain database sessions.
- **Service Layer**: The MCP server MUST use `TaskService` from `backend/src/services/task_service.py` for all task operations. This ensures business validation (title length, empty checks) is applied consistently.
- **Models**: The MCP server MUST use `TaskCreate`, `TaskUpdate`, `TaskRead` from `backend/src/models/task.py` for request/response shaping.
- **Environment**: The MCP server MUST read `DATABASE_URL` from environment variables, consistent with the existing backend configuration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: MCP server starts and is ready to accept tool calls within 30 seconds of launch.
- **SC-002**: All 5 tools respond to valid requests within 2 seconds (p95 latency).
- **SC-003**: `tools/list` returns exactly 5 tools, each with `name`, `description`, and complete `inputSchema`.
- **SC-004**: Each tool correctly enforces user isolation — calling with user A's ID never returns or modifies user B's tasks (verified by test).
- **SC-005**: Error cases (task not found, invalid input, empty title) return structured error content rather than crashing the server.
- **SC-006**: The MCP server can be connected to from the MCP Inspector tool and all 5 tools can be invoked interactively.
- **SC-007**: The MCP server can be registered as an MCP server in OpenAI Agents SDK configuration for use in Phase 3 Part 2.

### File Structure (Expected Output)

```
backend/
├── src/
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── server.py          # MCP server with 5 tool definitions
│   ├── models/
│   │   └── task.py             # Existing (unchanged)
│   ├── services/
│   │   └── task_service.py     # Existing (unchanged or minimally adapted)
│   └── database/
│       └── __init__.py         # Existing (unchanged)
```
