# Tasks: Phase 3 Part 1 — MCP Server and Tooling

**Feature**: MCP Server and Tooling
**Feature Branch**: `1-mcp-server-todo-tools`
**Created**: 2026-02-08
**Status**: Complete
**Spec**: [specs/1-mcp-server-todo-tools/spec.md](spec.md)
**Plan**: [specs/1-mcp-server-todo-tools/plan.md](plan.md)

## Phase 1: Dependency & Scaffold

### Goal
Install the MCP SDK dependency and create the `backend/src/mcp/` package skeleton with a runnable server entry point.

### Independent Test
`python -c "from mcp.server.fastmcp import FastMCP; print('OK')"` succeeds, and `python -m backend.src.mcp.server` starts without import errors (hangs on stdin, which is expected).

### Implementation Tasks

- [x] T001 Add `mcp[cli]>=1.26.0` to `backend/requirements.txt` and install it
  - **Precondition**: `backend/requirements.txt` exists
  - **Artifacts**: `backend/requirements.txt`
  - **Ref**: Plan Step 1, FR-001

- [x] T002 Create `backend/src/mcp/__init__.py` with empty package init
  - **Precondition**: `backend/src/` directory exists
  - **Artifacts**: `backend/src/mcp/__init__.py`
  - **Ref**: Plan Step 2, Spec File Structure

- [x] T003 Create `backend/src/mcp/server.py` with FastMCP skeleton — `FastMCP("todo-mcp-server")`, dotenv loading for `DATABASE_URL`, logging to stderr, `if __name__` entry point
  - **Precondition**: T001, T002
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: Plan Step 2, FR-001, FR-013

## Phase 2: Session Helper

### Goal
Create a reusable async context manager that provides a `TaskService` instance with a scoped database session, usable by every MCP tool handler.

### Independent Test
Import the helper and confirm it yields a `TaskService` instance without errors (requires `DATABASE_URL` set).

### Implementation Tasks

- [x] T004 Implement `get_task_service()` async context manager in `server.py` — wraps `AsyncSessionLocal()` and yields `TaskService(session)`
  - **Precondition**: T003
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: Plan Step 3, FR-009

## Phase 3: Core Tools — add_task & list_tasks (P1)

### Goal
Implement the two highest-priority tools that enable basic task creation and retrieval.

### Independent Test
Using MCP Inspector or direct function call: create a task with `add_task`, then retrieve it with `list_tasks` and verify the task appears in the returned array.

### Implementation Tasks

- [x] T005 [US1] Implement `add_task` tool — `@mcp.tool()` with params `user_id` (str, required), `title` (str, required), `description` (str, optional). Docstring: intent-based ("Use this when the user wants to add, create, or remember something as a task."). Calls `service.create_task_for_user()`. Returns JSON `{"task_id", "status": "created", "title"}`. Error handling: catch `ValueError` for empty/long title.
  - **Precondition**: T004
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: Plan Step 4, FR-003, Spec US1, ADR-003
  - **Acceptance**: Scenarios 1-3 from Spec US1

- [x] T006 [US2] Implement `list_tasks` tool — `@mcp.tool()` with params `user_id` (str, required), `status` (str, optional, default "all"). Validate status is one of "all", "pending", "completed". Map status to `is_completed` filter. Calls `service.get_tasks_by_user()` and filters in-memory if needed, or uses CRUD directly. Returns JSON array of task objects with `id`, `title`, `description`, `is_completed`, `created_at`.
  - **Precondition**: T004
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: Plan Step 5, FR-004, Spec US2, ADR-003
  - **Acceptance**: Scenarios 1-4 from Spec US2

## Phase 4: Remaining Tools — complete, delete, update (P2)

### Goal
Implement the three remaining tools for toggling completion, deleting tasks, and updating task details.

### Independent Test
Using MCP Inspector: complete a task (verify toggle), update a task's title, delete a task — each returns correct structured response.

### Implementation Tasks

- [x] T007 [US3] Implement `complete_task` tool — `@mcp.tool()` with params `user_id`, `task_id`. Calls `service.toggle_task_completion()`. Returns JSON `{"task_id", "status": "completed"|"pending", "title"}`. Error handling: catch `TaskOwnershipError` → "Task not found or access denied".
  - **Precondition**: T004
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: Plan Step 6, FR-005, Spec US3

- [x] T008 [US4] Implement `update_task` tool — `@mcp.tool()` with params `user_id`, `task_id`, `title` (optional), `description` (optional). Creates `TaskUpdate()` with provided fields. Calls `service.update_task_by_user()`. Returns JSON `{"task_id", "status": "updated", "title"}`. Edge case: if neither field provided, fetch and return current state.
  - **Precondition**: T004
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: Plan Step 8, FR-007, Spec US4

- [x] T009 [US5] Implement `delete_task` tool — `@mcp.tool()` with params `user_id`, `task_id`. Pre-fetch task to capture title before deletion. Calls `service.delete_task_by_user()`. Returns JSON `{"task_id", "status": "deleted", "title"}`. Error handling: catch `TaskOwnershipError`.
  - **Precondition**: T004
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: Plan Step 7, FR-006, Spec US5

## Phase 5: Tool Discovery & Error Handling

### Goal
Ensure all 5 tools appear in `tools/list` with correct schemas, and all error paths return structured `isError=True` content rather than crashing the server.

### Independent Test
Run MCP Inspector, call `tools/list` → verify exactly 5 tools with `name`, `description`, `inputSchema`. Call each tool with invalid inputs → verify structured error responses.

### Implementation Tasks

- [x] T010 [US6] Verify tool discovery — all 5 tools registered with `name`, `description`, `inputSchema` containing correct `required` arrays and property types matching `contracts/mcp-tools-schema.json`
  - **Precondition**: T005-T009
  - **Artifacts**: N/A (verification task)
  - **Ref**: FR-010, FR-011, Spec US6

- [x] T011 Review and harden error handling across all tools — ensure `TaskOwnershipError` (HTTPException subclass) is caught and converted to structured error content, `ValueError` returns clear messages, unexpected exceptions return "Internal error: ..." without crashing
  - **Precondition**: T005-T009
  - **Artifacts**: `backend/src/mcp/server.py`
  - **Ref**: FR-012, Spec Edge Cases, Plan Error Flow

## Phase 6: Integration Testing

### Goal
Validate the MCP server end-to-end using MCP Inspector and automated tests.

### Independent Test
MCP Inspector connects, lists tools, and all 5 tools can be invoked with valid and invalid inputs. Automated test suite passes.

### Implementation Tasks

- [x] T012 Manual integration test with MCP Inspector — run `npx @modelcontextprotocol/inspector python -m backend.src.mcp.server`, verify: tools/list returns 5 tools, add_task creates a task, list_tasks returns it, complete_task toggles status, update_task changes title, delete_task removes it
  - **Precondition**: T010, T011
  - **Artifacts**: N/A (manual verification)
  - **Ref**: Plan Step 9, SC-003, SC-006

- [x] T013 Create `backend/tests/test_mcp_server.py` — unit tests calling tool handler functions directly (bypassing MCP transport). Test: each tool with valid inputs, user isolation (user A cannot access user B's tasks), error cases (empty title, nonexistent task_id, invalid status value)
  - **Precondition**: T010, T011
  - **Artifacts**: `backend/tests/test_mcp_server.py`
  - **Ref**: Plan Step 10, SC-004, SC-005

## Dependencies

### Task Completion Order
1. T001-T003: Scaffold (sequential)
2. T004: Session helper (depends on T003)
3. T005-T009: Tool implementations (depend on T004, can be done in parallel)
4. T010-T011: Verification & hardening (depend on all tools)
5. T012-T013: Testing (depend on T010-T011)

### Critical Path
T001 → T002 → T003 → T004 → T005 → T010 → T012

### Parallel Execution
- T005 and T006 can run in parallel (both depend only on T004)
- T007, T008, T009 can run in parallel (all depend only on T004)
- T012 and T013 can run in parallel (both depend on T010-T011)

## Success Criteria Mapping

| Success Criterion | Validated By |
|-------------------|-------------|
| SC-001: Server starts within 30s | T003 |
| SC-002: Tool response <2s p95 | T012 |
| SC-003: tools/list returns 5 tools | T010 |
| SC-004: User isolation enforced | T013 |
| SC-005: Errors return structured content | T011, T013 |
| SC-006: MCP Inspector works | T012 |
| SC-007: Compatible with OpenAI Agents SDK | T003 (stdio transport) |
