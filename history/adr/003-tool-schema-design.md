# ADR-003: MCP Tool Schema Design — Descriptive Schemas for Agent Intelligence

**Date**: 2026-02-07
**Status**: Accepted
**Context**: Phase 3 Part 1 — MCP Server and Tooling

## Decision

Use Python type hints + docstrings with the FastMCP `@mcp.tool()` decorator to auto-generate tool schemas. Tool descriptions MUST explain "why" and "when" to call each tool (not just "what" it does) to enable accurate agent tool selection.

## Context

The AI agent (OpenAI Agents SDK) selects which MCP tool to call based on the tool's `name`, `description`, and `inputSchema`. If descriptions are vague or purely technical, the agent will make poor tool selections. The schema design directly impacts agent accuracy.

## Schema Design Principles

### 1. Tool Names — Action-oriented, Snake-case
- `add_task` (not `create_task` or `createTask`)
- `list_tasks` (not `get_tasks` or `view_tasks`)
- `complete_task` (not `toggle_completion`)
- `delete_task` (not `remove_task`)
- `update_task` (not `modify_task`)

Rationale: Names match the hackathon spec exactly. Snake_case is Python convention and MCP convention.

### 2. Tool Descriptions — Intent-Based for LLM Reasoning

Each description follows the pattern: **What it does** + **When to use it** + **What it returns**.

| Tool | Description |
|------|-------------|
| `add_task` | "Create a new todo task for a user. Use this when the user wants to add, create, or remember something as a task. Returns the created task's ID, status, and title." |
| `list_tasks` | "Retrieve all tasks for a user, optionally filtered by completion status. Use this when the user wants to see, show, or review their tasks. Returns an array of task objects." |
| `complete_task` | "Toggle the completion status of a task. If pending, becomes completed; if completed, reverts to pending. Use this when the user says they finished, completed, or are done with a task." |
| `delete_task` | "Permanently remove a task from the user's list. Use this when the user wants to delete, remove, or cancel a task. This action cannot be undone." |
| `update_task` | "Modify the title and/or description of an existing task. Use this when the user wants to change, rename, edit, or update a task's details. Only provided fields are updated." |

### 3. Parameter Descriptions — Context for the Agent

Every parameter has a description explaining its purpose:
- `user_id`: "The unique identifier of the user who owns the task" (not just "user id")
- `status`: "Filter by status: 'all' (default), 'pending' (incomplete only), or 'completed' (done only)"
- `task_id`: "The unique identifier of the task to [action]"

### 4. Return Format — Consistent JSON Strings

All tools return JSON strings (not raw dicts) to ensure consistent `TextContent` wrapping:
```json
{"task_id": "uuid", "status": "created|updated|deleted|completed|pending", "title": "..."}
```

`list_tasks` returns a JSON array:
```json
[{"id": "uuid", "title": "...", "description": "...", "is_completed": false, "created_at": "..."}]
```

### 5. Error Format — Structured and Agent-Readable

Errors use `CallToolResult(isError=True)` with clear messages:
```json
{"error": "Task not found or access denied"}
{"error": "Task title cannot be empty"}
{"error": "Invalid status filter. Valid values: all, pending, completed"}
```

## Options Considered

### Option A: Auto-generated Schemas via Type Hints (Selected)
- Python type hints → JSON Schema auto-generation by FastMCP.
- Docstrings → tool descriptions.
- **Pros**: DRY; schema always matches implementation; Pythonic; FastMCP handles conversion.
- **Cons**: Less control over exact JSON Schema output (but FastMCP's output is correct).

### Option B: Manual JSON Schema Definitions
- Define `inputSchema` dicts manually and register tools via low-level API.
- **Pros**: Full control over schema.
- **Cons**: Verbose; easy to get out of sync with implementation; not DRY.

### Option C: Pydantic Models for Parameters
- Define Pydantic models for each tool's input, pass to FastMCP.
- **Pros**: Explicit validation; reusable models.
- **Cons**: Over-engineered for 2-4 params per tool; adds model classes that mirror function signatures.

## Consequences

- Tool descriptions MUST be reviewed during testing to ensure the agent selects the correct tool for common natural language inputs.
- The contract file at `specs/1-mcp-server-todo-tools/contracts/mcp-tools-schema.json` serves as the reference schema; the implementation MUST match it.
- If agent accuracy is poor, the first remediation is to improve tool descriptions (not add more tools).
