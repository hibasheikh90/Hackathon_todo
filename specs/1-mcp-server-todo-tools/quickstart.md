# Quickstart: MCP Server and Tooling

**Feature**: `1-mcp-server-todo-tools` | **Date**: 2026-02-07

## Prerequisites

- Python 3.10+ installed
- Neon PostgreSQL database running (Phase 2 `DATABASE_URL` configured)
- Backend `.env` file with `DATABASE_URL` set

## Installation

```bash
cd backend
pip install "mcp[cli]"
```

Or add to `requirements.txt`:
```
mcp[cli]>=1.26.0
```

## Running the MCP Server

### Standalone (stdio mode for testing)

```bash
cd <project-root>
python -m backend.src.mcp.server
```

The server starts and listens on stdin/stdout for MCP protocol messages. You will not see output — it communicates via JSON-RPC.

### With MCP Inspector (interactive testing)

```bash
npx @modelcontextprotocol/inspector python -m backend.src.mcp.server
```

This opens a web UI at `http://localhost:5173` where you can:
1. See all 5 tools listed with their schemas
2. Invoke any tool with custom parameters
3. Inspect the JSON-RPC request/response payloads

### With OpenAI Agents SDK (Phase 3 Part 2)

```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    name="todo-tools",
    params={
        "command": "python",
        "args": ["-m", "backend.src.mcp.server"],
    },
) as server:
    # server.list_tools() returns all 5 tools
    # Agent can now call add_task, list_tasks, etc.
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string (same as Phase 2) |

The MCP server reads `DATABASE_URL` from the environment. The `.env` file in `backend/` is loaded automatically via `python-dotenv`.

## Verifying the Setup

1. **Start the server**: `python -m backend.src.mcp.server`
2. **Open MCP Inspector**: `npx @modelcontextprotocol/inspector python -m backend.src.mcp.server`
3. **Check tools**: Click "List Tools" — you should see 5 tools
4. **Test add_task**: Call `add_task` with `user_id` = a valid user UUID, `title` = "Test task"
5. **Test list_tasks**: Call `list_tasks` with the same `user_id` — the new task should appear
6. **Test complete_task**: Call `complete_task` with the `task_id` from step 4
7. **Test update_task**: Call `update_task` with a new title
8. **Test delete_task**: Call `delete_task` — the task should be removed

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: backend.src...` | Run from project root, not from `backend/` |
| `connection refused` on DB | Check `DATABASE_URL` in `.env`, ensure Neon DB is accessible |
| No output when running server | Expected! stdio servers communicate via JSON-RPC, not terminal output. Use MCP Inspector to interact. |
| `mcp` package not found | Run `pip install "mcp[cli]"` |
