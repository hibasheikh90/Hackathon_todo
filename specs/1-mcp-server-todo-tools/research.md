# Phase 0 Research: MCP Server and Tooling

**Feature**: `1-mcp-server-todo-tools` | **Date**: 2026-02-07

## Research 1: Official MCP Python SDK — API Patterns

**Decision**: Use `mcp` package v1.26+ with the `FastMCP` high-level API.

**Rationale**: FastMCP (integrated into the official SDK at `mcp.server.fastmcp.FastMCP`) provides a decorator-based tool definition API that auto-generates JSON Schema from Python type hints. This eliminates manual schema authoring and reduces boilerplate. It is the official, maintained approach — not a third-party fork.

**Alternatives considered**:
- **Low-level `mcp.server.Server`**: Requires manually constructing `Tool` objects with raw JSON Schema dicts. More verbose, no advantage for our use case.
- **Third-party `fastmcp` 2.0 package**: Separate project at `pip install fastmcp`. Adds proxy, composition, and OpenAPI features we don't need. Introduces an unnecessary dependency when the official SDK already includes FastMCP.

**Key API patterns**:

```python
from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("todo-mcp-server")

@mcp.tool()
async def add_task(user_id: str, title: str, description: str | None = None) -> str:
    """Create a new todo task for the specified user."""
    # ... implementation
    return json.dumps({"task_id": "uuid", "status": "created", "title": title})

if __name__ == "__main__":
    asyncio.run(mcp.run())  # stdio transport is default
```

**Tool parameters**: Defined via Python type annotations. Required params have no default; optional params have a default value. The SDK generates `inputSchema` automatically.

**Return values**: Tools can return `str`, `dict`, Pydantic models, or explicit `CallToolResult` objects. Returning a string is the simplest path; the SDK wraps it as `TextContent`.

**Error handling**: Return `CallToolResult(isError=True, content=[TextContent(type="text", text="error message")])` for tool-level errors that the agent should see. Unhandled exceptions crash the connection.

**Install**: `pip install "mcp[cli]"` (requires Python >=3.10).

---

## Research 2: MCP Transport — Stdio vs HTTP/SSE

**Decision**: Use **stdio transport** for this phase.

**Rationale**: The OpenAI Agents SDK connects to MCP servers via `MCPServerStdio`, which spawns the server as a subprocess and communicates over stdin/stdout. This is the simplest, most compatible approach for:
- Local development and testing
- MCP Inspector verification
- OpenAI Agents SDK integration (Phase 3 Part 2)
- Claude Desktop compatibility (bonus)

**Alternatives considered**:
- **HTTP/SSE transport** (`streamable-http`): Would require running the MCP server as a standalone HTTP service on a port. Adds networking complexity, CORS handling, and port management. Useful for remote/distributed deployments but overkill for Phase 3 where the agent and MCP server co-locate in the same backend process (or subprocess).
- **SSE (legacy)**: Deprecated in favor of `streamable-http`. Not recommended.

**Critical stdio constraint**: Tools MUST NOT write to stdout (it corrupts JSON-RPC messages). All logging MUST go to stderr via Python's `logging` module.

---

## Research 3: Database Session Management in MCP Context

**Decision**: Create an async session per tool call using `AsyncSessionLocal()` as a context manager.

**Rationale**: The MCP server runs as a standalone Python process (not inside FastAPI). It cannot use FastAPI's `Depends()` injection. Instead, each tool creates its own session:

```python
async with AsyncSessionLocal() as session:
    service = TaskService(session)
    result = await service.create_task_for_user(task_data, user_id)
```

This is safe because:
- `AsyncSessionLocal` is a `sessionmaker` bound to the same `async_engine` as FastAPI
- Each tool call gets an isolated transaction
- Sessions are closed after each call (no leaks)

**Alternatives considered**:
- **Calling FastAPI REST endpoints via HTTP**: Would require the FastAPI server to be running, adds network latency, and requires JWT auth handling between MCP server and FastAPI. Unnecessarily complex when direct DB access is available.
- **Global session**: Dangerous — shared mutable state across concurrent tool calls. Rejected.

---

## Research 4: Authentication Bridge — MCP ↔ User Identity

**Decision**: The `user_id` parameter is passed explicitly in every tool call. The chat endpoint (Phase 3 Part 2) is responsible for extracting `user_id` from the JWT and injecting it into tool calls.

**Rationale**: In the Phase 3 architecture:
1. User authenticates with Better Auth → receives JWT
2. Frontend sends message to `POST /api/{user_id}/chat` with JWT header
3. FastAPI chat endpoint validates JWT, confirms `user_id` matches
4. FastAPI instantiates the OpenAI Agent with `user_id` baked into the system prompt
5. Agent calls MCP tools, always passing `user_id` as a parameter
6. MCP tools enforce `user_id` at the database query level (WHERE user_id = ?)

The MCP server itself does NOT validate JWTs — it trusts the `user_id` parameter because:
- The MCP server runs as a subprocess of the authenticated FastAPI process
- Only the chat endpoint can invoke the MCP server (not end users directly)
- User isolation is enforced at the SQL level regardless

**Alternatives considered**:
- **JWT validation inside MCP tools**: Would require sharing `BETTER_AUTH_SECRET` with the MCP process and adding jose/jwt dependencies. Adds complexity without security benefit since the MCP server is not externally accessible.
- **MCP server as HTTP service with auth middleware**: Would expose the MCP server as a network endpoint requiring its own auth. Contradicts the stdio architecture decision.

---

## Research 5: OpenAI Agents SDK ↔ MCP Integration

**Decision**: Use `MCPServerStdio` from `agents.mcp` to connect the OpenAI Agent to the MCP server.

**Rationale**: The OpenAI Agents SDK provides a first-class MCP integration:

```python
from agents.mcp import MCPServerStdio
from agents import Agent, Runner

async with MCPServerStdio(
    name="todo-tools",
    params={
        "command": "python",
        "args": ["-m", "backend.src.mcp.server"],
    },
) as server:
    agent = Agent(
        name="Todo Assistant",
        instructions="...",
        mcp_servers=[server],
    )
    result = await Runner.run(agent, "Add a task to buy groceries")
```

- `MCPServerStdio` spawns the MCP server as a subprocess
- Tools are auto-discovered via `tools/list`
- Tool schemas and descriptions are forwarded to the LLM
- The Agent decides when to call which tool based on natural language

**Install**: `pip install openai-agents` (for Phase 3 Part 2).

---

## Research 6: TaskService Compatibility with MCP

**Decision**: Reuse `TaskService` directly with one adaptation — catch `TaskOwnershipError` (which is an `HTTPException` subclass) and convert to structured error strings.

**Rationale**: `TaskService` methods raise `TaskOwnershipError` (inherits from `fastapi.HTTPException`). In the MCP context, we don't have FastAPI's exception handler. The MCP tool wrapper MUST catch these exceptions and return them as error content:

```python
try:
    result = await service.delete_task_by_user(task_id, user_id)
except TaskOwnershipError:
    return CallToolResult(isError=True, content=[TextContent(type="text", text="Task not found or access denied")])
except ValueError as e:
    return CallToolResult(isError=True, content=[TextContent(type="text", text=str(e))])
```

No changes to `TaskService` itself are needed. The MCP layer adapts the error handling.

**Alternatives considered**:
- **Modify TaskService to raise non-HTTP exceptions**: Would require refactoring Phase 2 code that already works. Violates the principle of minimal change.
- **Create a separate MCP-specific service layer**: Duplicates logic. Violates FR-009 (reuse existing infrastructure).
