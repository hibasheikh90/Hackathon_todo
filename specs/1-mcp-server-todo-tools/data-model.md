# Data Model: MCP Server and Tooling

**Feature**: `1-mcp-server-todo-tools` | **Date**: 2026-02-07

## Entities

This feature introduces NO new database entities. It reuses the existing Phase 2 models.

### Existing Entity: Task (unchanged)

**Source**: `backend/src/models/task.py`

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | string (UUID) | PK, auto-generated | `uuid.uuid4()` |
| `title` | string | NOT NULL, 1-255 chars | Required |
| `description` | string | nullable, max 10000 | Optional |
| `is_completed` | boolean | default `false` | Toggle via `complete_task` |
| `user_id` | string (UUID) | FK → users.id, NOT NULL, indexed | User isolation key |
| `created_at` | datetime | NOT NULL, auto-generated | UTC |
| `updated_at` | datetime | NOT NULL, auto-updated | UTC |

### Existing Entity: User (unchanged)

**Source**: `backend/src/models/user.py`

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | string (UUID) | PK, auto-generated | User identity for MCP tools |
| `email` | string | UNIQUE, NOT NULL | Not used by MCP tools |
| `password_hash` | string | NOT NULL | Not used by MCP tools |
| `is_active` | boolean | default `true` | Not checked by MCP tools |
| `created_at` | datetime | NOT NULL | Not used by MCP tools |
| `updated_at` | datetime | NOT NULL | Not used by MCP tools |

## MCP Tool Input/Output Schemas

These are NOT database entities but define the contract between the AI agent and the MCP server.

### add_task Input

```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "The ID of the user creating the task"},
    "title": {"type": "string", "description": "The title of the task (1-255 characters)"},
    "description": {"type": "string", "description": "Optional description of the task"}
  },
  "required": ["user_id", "title"]
}
```

### add_task Output

```json
{"task_id": "uuid-string", "status": "created", "title": "Buy groceries"}
```

### list_tasks Input

```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "The ID of the user whose tasks to list"},
    "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter tasks by status. Defaults to 'all'"}
  },
  "required": ["user_id"]
}
```

### list_tasks Output

```json
[
  {
    "id": "uuid-string",
    "title": "Buy groceries",
    "description": "Milk, eggs",
    "is_completed": false,
    "created_at": "2026-02-07T10:00:00"
  }
]
```

### complete_task Input

```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "The ID of the user who owns the task"},
    "task_id": {"type": "string", "description": "The ID of the task to mark complete/incomplete"}
  },
  "required": ["user_id", "task_id"]
}
```

### complete_task Output

```json
{"task_id": "uuid-string", "status": "completed", "title": "Buy groceries"}
```

(or `"status": "pending"` if toggled back)

### delete_task Input

```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "The ID of the user who owns the task"},
    "task_id": {"type": "string", "description": "The ID of the task to delete"}
  },
  "required": ["user_id", "task_id"]
}
```

### delete_task Output

```json
{"task_id": "uuid-string", "status": "deleted", "title": "Buy groceries"}
```

### update_task Input

```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "The ID of the user who owns the task"},
    "task_id": {"type": "string", "description": "The ID of the task to update"},
    "title": {"type": "string", "description": "New title for the task"},
    "description": {"type": "string", "description": "New description for the task"}
  },
  "required": ["user_id", "task_id"]
}
```

### update_task Output

```json
{"task_id": "uuid-string", "status": "updated", "title": "Buy groceries and fruits"}
```

### Error Output (all tools)

```json
{"error": "Task not found or access denied"}
```

Returned via `CallToolResult(isError=True, content=[TextContent(...)])`.

## State Transitions

```
Task.is_completed: false ──complete_task──► true
Task.is_completed: true  ──complete_task──► false  (toggle)
```

No other state machine — tasks are created, optionally updated, and deleted.
