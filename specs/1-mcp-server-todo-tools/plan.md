# Implementation Plan: Phase 3 Part 1 — MCP Server and Tooling

**Branch**: `1-mcp-server-todo-tools` | **Date**: 2026-02-07 | **Spec**: `specs/1-mcp-server-todo-tools/spec.md`
**Input**: Feature specification from `specs/1-mcp-server-todo-tools/spec.md`

## Summary

Build an MCP server using the Official MCP SDK for Python (`mcp` package, FastMCP API) that exposes 5 todo-management tools (`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`) to AI agents. The server reuses the existing Phase 2 `TaskService` and `AsyncSessionLocal` for database operations, runs on stdio transport, and is designed for integration with the OpenAI Agents SDK via `MCPServerStdio` in Phase 3 Part 2.

## Technical Context

**Language/Version**: Python 3.13+ (matching Phase 2)
**Primary Dependencies**: `mcp[cli]>=1.26.0` (Official MCP SDK with FastMCP), existing `sqlmodel`, `asyncpg`, `sqlalchemy`
**Storage**: Neon Serverless PostgreSQL via existing `AsyncSessionLocal` (no new tables)
**Testing**: pytest with async support, MCP Inspector for manual verification
**Target Platform**: Local development (stdio subprocess), future Kubernetes (Phase IV)
**Project Type**: Backend extension (monorepo — `backend/src/mcp/`)
**Performance Goals**: Tool response <2s p95, server startup <30s
**Constraints**: Stdio transport only (no stdout writes); reuse Phase 2 service layer; no new database entities
**Scale/Scope**: 5 tools, 1 server module, ~200 lines of implementation code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. SDD** | PASS | Spec created at `specs/1-mcp-server-todo-tools/spec.md` before any code |
| **II. AI-Native** | PASS | All implementation via Claude Code |
| **III. Reusable Intelligence** | PASS | MCP tools are self-contained, reusable by any MCP client |
| **IV. Full-Stack Integration** | PASS | Uses Official MCP SDK; integrates with existing FastAPI/SQLModel/Neon stack |
| **V. Security-First** | PASS | `user_id` required on every tool; SQL-level isolation; ADR-002 documents auth bridge |
| **VI. Cloud-Native** | PASS | Stateless tool calls; no in-memory state; stdio compatible with containerization |
| **VII. MCP-First** | PASS | Exactly 5 tools via Official MCP SDK; agents use tools exclusively |
| **VIII. Stateless AI** | N/A | Conversation persistence is Phase 3 Part 2 scope |
| **IX. Agent Behavior** | PARTIAL | Tool descriptions designed for agent reasoning (ADR-003); agent config is Part 2 |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/1-mcp-server-todo-tools/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research decisions
├── data-model.md        # Existing entities + MCP tool schemas
├── quickstart.md        # Setup and run instructions
├── contracts/
│   └── mcp-tools-schema.json  # Tool input/output JSON Schema contract
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── mcp/
│   │   ├── __init__.py          # Package init, exports run_server()
│   │   └── server.py            # FastMCP server + 5 tool definitions
│   ├── models/
│   │   └── task.py              # Existing (UNCHANGED)
│   ├── services/
│   │   └── task_service.py      # Existing (UNCHANGED)
│   ├── database/
│   │   ├── __init__.py          # Existing (UNCHANGED)
│   │   └── async_utils.py       # Existing (UNCHANGED)
│   └── errors/
│       └── task_errors.py       # Existing (UNCHANGED)
├── tests/
│   └── test_mcp_server.py       # MCP tool unit tests
├── requirements.txt             # Add: mcp[cli]>=1.26.0
└── .env                         # Existing (UNCHANGED)
```

**Structure Decision**: Extend the existing backend with a new `mcp/` package. No new top-level directories. All 5 tools live in a single `server.py` file (~200 lines) because they are cohesive and share the same session/service pattern.

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Process                        │
│                    (python -m backend.src.mcp.server)        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              FastMCP("todo-mcp-server")                │  │
│  │                                                       │  │
│  │  @mcp.tool() add_task(user_id, title, description?)   │  │
│  │  @mcp.tool() list_tasks(user_id, status?)             │  │
│  │  @mcp.tool() complete_task(user_id, task_id)          │  │
│  │  @mcp.tool() delete_task(user_id, task_id)            │  │
│  │  @mcp.tool() update_task(user_id, task_id, ...)       │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Session Management Layer                  │  │
│  │                                                       │  │
│  │  async with AsyncSessionLocal() as session:           │  │
│  │      service = TaskService(session)                   │  │
│  │      result = await service.<method>(...)             │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         TaskService (from backend.src.services)       │  │
│  │                                                       │  │
│  │  create_task_for_user()  →  async_task_crud           │  │
│  │  get_tasks_by_user()     →  async_task_crud           │  │
│  │  toggle_task_completion() →  async_task_crud          │  │
│  │  update_task_by_user()   →  async_task_crud           │  │
│  │  delete_task_by_user()   →  async_task_crud           │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │ asyncpg
                            ▼
                   ┌─────────────────┐
                   │  Neon PostgreSQL │
                   │  (tasks table)  │
                   └─────────────────┘
```

### Data Flow — Single Tool Call

```
stdin → JSON-RPC request
  → FastMCP deserializes, validates inputSchema
    → @mcp.tool() handler executes
      → AsyncSessionLocal() creates DB session
        → TaskService.<method>() runs business logic
          → async_task_crud queries Neon PostgreSQL
        → Result returned as Task object
      → Session closed
    → Handler formats JSON string response
  → FastMCP wraps as TextContent
→ JSON-RPC response on stdout
```

### Error Flow

```
Tool handler catches:
  ├── TaskOwnershipError → CallToolResult(isError=True, "Task not found or access denied")
  ├── ValueError         → CallToolResult(isError=True, str(e))
  └── Exception          → CallToolResult(isError=True, "Internal error: ...")
```

## Implementation Roadmap

### Step 1: Dependency Setup
- Add `mcp[cli]>=1.26.0` to `backend/requirements.txt`
- Create `backend/src/mcp/__init__.py` and `backend/src/mcp/server.py`
- Verify `python -c "from mcp.server.fastmcp import FastMCP; print('OK')"` works

### Step 2: MCP Server Skeleton
- Create `FastMCP("todo-mcp-server")` instance in `server.py`
- Add `dotenv` loading for `DATABASE_URL`
- Add `if __name__ == "__main__": asyncio.run(mcp.run())` entry point
- Configure logging to stderr (NOT stdout)
- Verify server starts: `python -m backend.src.mcp.server` (should hang waiting for stdin)

### Step 3: Session Helper
- Create an async context-manager helper to provide `TaskService` instances:
  ```python
  @asynccontextmanager
  async def get_task_service():
      async with AsyncSessionLocal() as session:
          yield TaskService(session)
  ```
- This pattern is used by every tool to get a scoped session + service

### Step 4: Implement `add_task` Tool (FR-003)
- `@mcp.tool()` decorator with type hints for `user_id`, `title`, `description`
- Docstring explains when to use the tool
- Creates `TaskCreate(title=title, description=description)`
- Calls `service.create_task_for_user(task_data, user_id)`
- Returns JSON: `{"task_id": task.id, "status": "created", "title": task.title}`
- Error handling: catch `ValueError` for empty title / length violations

### Step 5: Implement `list_tasks` Tool (FR-004)
- Parameters: `user_id`, `status` (default "all")
- Validates `status` is one of "all", "pending", "completed"
- Maps status to `completed` filter: "all" → None, "pending" → False, "completed" → True
- Calls `async_task_crud.get_tasks_by_user(session, user_id, completed=filter_value)`
  (Note: uses CRUD directly instead of TaskService since TaskService.get_tasks_by_user doesn't support the `completed` filter)
- Returns JSON array of task objects

### Step 6: Implement `complete_task` Tool (FR-005)
- Parameters: `user_id`, `task_id`
- Calls `service.toggle_task_completion(task_id, user_id)`
- Returns JSON with status "completed" or "pending" based on new `is_completed` value
- Error handling: catch `TaskOwnershipError` → "Task not found or access denied"

### Step 7: Implement `delete_task` Tool (FR-006)
- Parameters: `user_id`, `task_id`
- Fetch task first to capture title before deletion
- Calls `service.delete_task_by_user(task_id, user_id)`
- Returns JSON: `{"task_id": task_id, "status": "deleted", "title": title}`
- Error handling: catch `TaskOwnershipError`

### Step 8: Implement `update_task` Tool (FR-007)
- Parameters: `user_id`, `task_id`, `title` (optional), `description` (optional)
- Creates `TaskUpdate()` with only provided fields
- Calls `service.update_task_by_user(task_id, task_data, user_id)`
- Returns JSON: `{"task_id": task_id, "status": "updated", "title": updated.title}`
- Edge case: if neither `title` nor `description` provided, fetch and return current state

### Step 9: Integration Testing with MCP Inspector
- Run: `npx @modelcontextprotocol/inspector python -m backend.src.mcp.server`
- Verify `tools/list` returns all 5 tools with correct schemas
- Test each tool manually with valid and invalid inputs
- Verify error cases return `isError=true` content

### Step 10: Automated Tests
- Create `backend/tests/test_mcp_server.py`
- Test each tool function directly (bypassing MCP transport)
- Test with real database connection (integration tests)
- Test user isolation: user A's tools cannot access user B's tasks
- Test error cases: empty title, nonexistent task_id, invalid status

## Key Architectural Decisions

| Decision | ADR | Summary |
|----------|-----|---------|
| Stdio transport | [ADR-001](../../history/adr/001-mcp-transport-stdio.md) | MCP server uses stdio; spawned as subprocess by OpenAI Agents SDK |
| User ID passthrough | [ADR-002](../../history/adr/002-auth-bridge-user-id-passthrough.md) | JWT validated at FastAPI endpoint; user_id passed as tool parameter |
| Descriptive tool schemas | [ADR-003](../../history/adr/003-tool-schema-design.md) | Type hints + intent-based docstrings for agent tool selection |

## Mapping: FastAPI Endpoints → MCP Tools

| Phase 2 REST Endpoint | MCP Tool | Service Method | Notes |
|----------------------|----------|---------------|-------|
| `POST /api/tasks` | `add_task` | `TaskService.create_task_for_user()` | Same validation |
| `GET /api/tasks` | `list_tasks` | `async_task_crud.get_tasks_by_user()` | Direct CRUD for filter support |
| `PATCH /api/tasks/{id}/complete` | `complete_task` | `TaskService.toggle_task_completion()` | Same toggle logic |
| `DELETE /api/tasks/{id}` | `delete_task` | `TaskService.delete_task_by_user()` | Pre-fetch for title |
| `PUT /api/tasks/{id}` | `update_task` | `TaskService.update_task_by_user()` | Same partial update |

## Dependencies (New)

| Package | Version | Purpose |
|---------|---------|---------|
| `mcp[cli]` | >=1.26.0 | Official MCP SDK with FastMCP and CLI tools |

No other new dependencies. All database, model, and service imports are from existing Phase 2 code.

## Risks

1. **Import path issues**: The MCP server runs as a separate process. Python import paths (`backend.src.models.*`) must resolve correctly. Mitigation: use `python -m backend.src.mcp.server` from the project root, and ensure `sys.path` includes the project root.

2. **Async session lifecycle in non-FastAPI context**: `AsyncSessionLocal` was designed for FastAPI's dependency injection. Running it standalone requires manual context management. Mitigation: the `get_task_service()` context manager handles this explicitly.

3. **TaskOwnershipError inherits HTTPException**: In the MCP context, there is no HTTP response to send. If not caught, it would crash the tool. Mitigation: every tool handler wraps service calls in try/except for `TaskOwnershipError` and `ValueError`.
