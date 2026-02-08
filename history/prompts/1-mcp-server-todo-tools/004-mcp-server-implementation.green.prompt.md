---
id: 004
title: MCP Server Implementation
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 1-mcp-server-todo-tools
branch: main
user: hayas
command: /sp.implement
labels: ["phase3", "mcp", "implementation", "green"]
links:
  spec: specs/1-mcp-server-todo-tools/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/src/mcp/__init__.py
  - backend/src/mcp/server.py
  - backend/tests/test_mcp_server.py
  - backend/src/database/async_utils.py
tests:
  - backend/tests/test_mcp_server.py (21 tests, 21 passed)
---

## Prompt

/sp.implement

## Response snapshot

Implemented the full MCP server for Phase 3 Part 1, completing all 13 tasks (T001-T013):

**T001-T003: Scaffold**
- Added `mcp[cli]>=1.26.0` to `backend/requirements.txt`
- Created `backend/src/mcp/__init__.py` package
- Created `backend/src/mcp/server.py` with FastMCP skeleton, dotenv loading, stderr logging, stdio transport

**T004: Session Helper**
- Implemented `get_task_service()` async context manager wrapping `AsyncSessionLocal` + `TaskService`

**T005-T009: All 5 MCP Tools**
- `add_task` — creates tasks with title validation, returns `{task_id, status, title}`
- `list_tasks` — retrieves tasks with status filtering (all/pending/completed)
- `complete_task` — toggles completion with ownership check
- `update_task` — partial update with no-op edge case handling
- `delete_task` — pre-fetches title before deletion with ownership check

**T010-T011: Tool Discovery & Error Hardening**
- Verified 5 tools registered with correct schemas
- All tools handle TaskOwnershipError, ValueError, and unexpected exceptions with structured JSON errors

**T012-T013: Testing**
- Created `backend/tests/test_mcp_server.py` with 21 automated tests across 5 test classes
- Tests cover: valid operations, empty title, invalid status, user isolation, nonexistent tasks, cross-user access

**Bug Fixes Discovered During Implementation:**
1. Phase 2 bug in `async_utils.py:265` — `db.delete(db_task)` was not awaited (coroutine never awaited). Fixed: `await db.delete(db_task)`
2. `update_task` with description-only update failed because `TaskUpdate(title=None, description="...")` triggered validation on the None title. Fixed by building `TaskUpdate(**update_fields)` with only provided fields.

**Testing Challenges Overcome:**
- SQLAlchemy duplicate table registration from dual import paths (`src.*` vs `backend.src.*`) — solved with module aliasing
- Foreign key constraints for test users — solved with session-scoped fixture inserting test users
- Event loop lifecycle issues — solved with `loop_scope="session"` for pytest-asyncio

## Outcome

- Impact: Complete MCP server with 5 tools, all tested end-to-end against real database
- Tests: 21/21 passing (3 add, 6 list, 4 complete, 5 update, 3 delete)
- Files: 5 files created/modified
- Next prompts: Phase 3 Part 2 — OpenAI Agents SDK integration, chat endpoint, ChatKit UI
- Reflection: The main complexity was not the MCP server itself (~230 LOC) but the testing infrastructure — module aliasing for dual import paths, event loop management, and discovering Phase 2 bugs (unawaited db.delete, TaskUpdate validation). The server.py implementation was straightforward thanks to FastMCP's decorator-based API.

## Evaluation notes (flywheel)

- Failure modes observed: Phase 2 async bug (db.delete not awaited), TaskUpdate validation when title=None but explicitly set
- Graders run and results (PASS/FAIL): 21/21 PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Manual MCP Inspector validation to confirm stdio transport works end-to-end
