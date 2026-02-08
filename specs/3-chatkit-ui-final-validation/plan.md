# Implementation Plan: Phase 3 Part 3 — ChatKit UI and Final System Validation Architecture

**Branch**: `3-chatkit-ui-final-validation` | **Date**: 2026-02-08 | **Spec**: `specs/3-chatkit-ui-final-validation/spec.md`
**Input**: Feature specification from `specs/3-chatkit-ui-final-validation/spec.md`

## Summary

Build a conversational chat UI using the OpenAI ChatKit Python SDK (self-hosted mode) and `@openai/chatkit-react` frontend package. The system replaces the current synchronous `POST /api/chat` endpoint with a ChatKit-compatible streaming endpoint (`POST /api/chatkit`) that the React ChatKit component connects to directly. The backend implements a `ChatKitServer` subclass that integrates with the existing OpenAI Agents SDK agent and database-backed conversation persistence. The frontend embeds the ChatKit React component as a floating panel accessible from all authenticated pages. Final end-to-end validation confirms the full stack: ChatKit UI → ChatKit Server → Agent → MCP Tools → Database.

## Technical Context

**Language/Version**: TypeScript 5+ (frontend), Python 3.13+ (backend)
**Primary Dependencies (NEW)**:
- Frontend: `@openai/chatkit-react@^1.4.3` — React wrapper for ChatKit web component
- Backend: `chatkit` (PyPI) — ChatKit Python SDK for self-hosted server
**Existing Dependencies (UNCHANGED)**: `openai-agents>=0.8.0`, `mcp[cli]`, `sqlmodel`, `asyncpg`, `next@16.1.6`, `react@19.2.3`, `tailwindcss@4`
**Storage**: Neon Serverless PostgreSQL — existing `conversations` and `messages` tables (reused, no schema changes)
**Testing**: Frontend manual testing (ChatKit is a web component); backend integration tests for the ChatKit endpoint
**Target Platform**: Local development, future Kubernetes (Phase IV)
**Project Type**: Full-stack feature — new backend endpoint + new frontend components
**Performance Goals**: Chat panel open <100ms; streaming response starts within 5s; 100+ message history renders without lag
**Constraints**: Self-hosted ChatKit mode (not OpenAI-hosted); existing `POST /api/chat` endpoint preserved for backward compatibility; JWT auth must flow through ChatKit; MCP server unchanged from Part 1
**Scale/Scope**: ~1 new backend endpoint, ~7 new frontend files, ~500 lines of new code

## Constitution Check

*GATE: Must pass before implementation. Re-checked after design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. SDD** | PASS | Spec at `specs/3-chatkit-ui-final-validation/spec.md` precedes all code |
| **II. AI-Native** | PASS | All implementation via Claude Code |
| **III. Reusable Intelligence** | PASS | ChatKit component is self-contained; ChatContext is reusable |
| **IV. Full-Stack Integration** | PASS | Uses OpenAI ChatKit + Next.js + FastAPI + Agents SDK + MCP + Neon |
| **V. Security-First** | PASS | JWT validated at ChatKit endpoint; user_id injected into agent; no new attack surface |
| **VI. Cloud-Native** | PASS | Stateless ChatKit server; all state in database; ChatKit threads map to conversations |
| **VII. MCP-First** | PASS | Agent uses MCP tools exclusively; UI shows tool badges via ChatKit events |
| **VIII. Stateless AI** | PASS | ChatKit server loads thread from DB per request; no in-memory state |
| **IX. Agent Behavior** | PASS | Tool transparency via ChatKit annotations; error clarity via ChatKit error events |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/3-chatkit-ui-final-validation/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Created by /sp.tasks (next step)
```

### Source Code Changes

```text
backend/
├── src/
│   ├── api/
│   │   ├── chatkit_endpoint.py     # NEW: POST /api/chatkit — ChatKit server endpoint
│   │   ├── chat.py                 # Existing (UNCHANGED — kept for backward compat)
│   │   └── ...
│   ├── chatkit/
│   │   ├── __init__.py             # NEW: Package init
│   │   ├── server.py               # NEW: ChatKitServer subclass
│   │   └── store.py                # NEW: Database-backed ChatKit store
│   ├── agent/
│   │   └── todo_agent.py           # Existing (UNCHANGED)
│   ├── mcp/
│   │   └── server.py               # Existing (UNCHANGED, Part 1)
│   └── main.py                     # UPDATED: register chatkit router
├── tests/
│   ├── test_chatkit_endpoint.py    # NEW: ChatKit endpoint tests
│   └── ...                         # Existing tests (UNCHANGED)
└── requirements.txt                # UPDATED: add chatkit

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # UPDATED: add ChatKit script tag + ChatProvider
│   │   ├── dashboard/page.tsx      # Existing (UNCHANGED)
│   │   └── tasks/page.tsx          # Existing (UNCHANGED)
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatFAB.tsx         # NEW: Floating action button
│   │   │   ├── ChatPanel.tsx       # NEW: ChatKit wrapper panel
│   │   │   └── ChatLayout.tsx      # NEW: Auth-aware chat layout wrapper
│   │   └── tasks/                  # Existing (UNCHANGED)
│   ├── contexts/
│   │   ├── AuthContext.tsx          # Existing (UNCHANGED)
│   │   └── ChatContext.tsx          # NEW: Chat panel open/close state
│   └── lib/
│       ├── api.ts                   # Existing (UNCHANGED)
│       └── chat-types.ts            # NEW: TypeScript types for chat
└── package.json                     # UPDATED: add @openai/chatkit-react
```

**Structure Decision**: ChatKit Python SDK provides the `ChatKitServer` abstraction, which handles the streaming protocol, thread management, and event serialization. We subclass it with our existing database store and agent. The frontend uses `@openai/chatkit-react` which wraps the `<openai-chatkit>` web component — we configure it to point to our self-hosted `/api/chatkit` endpoint. This is simpler than building a custom streaming UI from scratch while still giving us full control over the backend logic.

## Architecture

### Component Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                         │
│                                                            │
│  ┌──────────┐  ┌──────────────────────────────────────┐   │
│  │ ChatFAB  │  │  ChatPanel                           │   │
│  │ (toggle) │─▶│  ┌──────────────────────────────────┐│   │
│  └──────────┘  │  │  <ChatKit>                       ││   │
│                │  │  @openai/chatkit-react            ││   │
│                │  │                                   ││   │
│                │  │  api.url = "/api/chatkit"         ││   │
│                │  │  api.headers = {Authorization}    ││   │
│                │  └──────────────────────────────────┘│   │
│                └───────────────┬──────────────────────┘   │
│                                │ SSE stream                │
└────────────────────────────────┼───────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────┐
│                    FastAPI Server                           │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  POST /api/chatkit                                    │ │
│  │  Depends(get_current_user) → User.id                  │ │
│  │                                                       │ │
│  │  result = await chatkit_server.process(body, ctx)     │ │
│  │  return StreamingResponse(result)                     │ │
│  └──────────────────────┬────────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  TodoChatKitServer(ChatKitServer)                     │ │
│  │                                                       │ │
│  │  store = DatabaseChatKitStore (conversations+messages)│ │
│  │                                                       │ │
│  │  async def respond(thread, items, context):           │ │
│  │    user_id = context["user_id"]                       │ │
│  │    input_items = convert_to_agent_format(items)       │ │
│  │    result = await run_agent(user_id, input_items)     │ │
│  │    yield ThreadStreamEvent(text=result.final_output)  │ │
│  └──────────────────────┬────────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  TodoAgent (OpenAI Agents SDK) — UNCHANGED            │ │
│  │  run_agent(user_id, input_items) → RunResult          │ │
│  └──────────────────────┬────────────────────────────────┘ │
│                          │ stdio                            │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  MCP Server (Part 1 — UNCHANGED)                      │ │
│  │  add_task, list_tasks, complete_task, delete_task,     │ │
│  │  update_task                                          │ │
│  └──────────────────────┬────────────────────────────────┘ │
│                          │ asyncpg                          │
└──────────────────────────┼──────────────────────────────────┘
                           ▼
                 ┌──────────────────┐
                 │  Neon PostgreSQL  │
                 │  - users         │
                 │  - tasks         │
                 │  - conversations │
                 │  - messages      │
                 └──────────────────┘
```

### Decision Point: ChatKit Integration Strategy

There are two approaches to integrating ChatKit with our existing system:

#### Option A: Full ChatKit Protocol (Selected)

Use the ChatKit Python SDK (`ChatKitServer`) on the backend and `@openai/chatkit-react` on the frontend. The ChatKit SDK handles:
- Thread/message management protocol
- Streaming via SSE (Server-Sent Events)
- Client-server event serialization
- Tool call annotations in the stream

**Pros**: Production-quality streaming out of the box; official OpenAI component handles UX details (thinking indicators, scroll management, message rendering); aligns with constitution requirement for "OpenAI ChatKit"; significantly less custom frontend code.

**Cons**: Adds `chatkit` Python package dependency; must adapt our database models to the ChatKit store interface; ChatKit web component has its own styling (customizable but opinionated).

#### Option B: Custom Chat UI with Direct API Calls

Build chat components from scratch (ChatMessages, ChatInput, ToolBadge, etc.) and call `POST /api/chat` directly.

**Pros**: Full control over UI; no new backend dependency; no learning curve.

**Cons**: Must implement streaming from scratch (SSE or WebSocket); must build thinking indicators, auto-scroll, markdown rendering, error handling manually; ~3x more frontend code; does NOT use ChatKit (violates constitution Principle IV which specifies "OpenAI ChatKit for conversational UI").

**Decision**: Option A. The constitution mandates ChatKit, and the official SDK provides streaming, message rendering, and tool transparency with minimal custom code.

### Data Flow — ChatKit Request Lifecycle

```
User clicks Send in ChatKit panel
  → <ChatKit> component POST /api/chatkit (Authorization: Bearer <jwt>)
    → FastAPI: get_current_user(jwt) → User object (or 401)
      → chatkit_server.process(body, context={"user_id": user_id})
        → ChatKitServer routes to respond() method
          → Load thread items from DatabaseChatKitStore (conversations + messages)
          → Convert thread items to agent input format
          → run_agent(user_id, input_items)
            → MCPServerStdio spawns MCP subprocess
              → LLM reasons → calls MCP tools with user_id
              → MCP tool → TaskService → Neon DB → result
            → RunResult with final_output + tool_calls
          → yield ThreadStreamEvent with response text
          → yield ThreadStreamEvent with tool call annotations
        → ChatKitServer serializes to SSE stream
      → StreamingResponse(text/event-stream)
    → <ChatKit> component renders streamed messages
      → User bubble (already shown optimistically)
      → "Agent is thinking..." (built-in ChatKit behavior)
      → Assistant bubble with response text
      → Tool badges from annotations
```

### Error Flow

```
ChatKit endpoint catches:
  ├── JWT invalid/expired       → HTTP 401 → ChatKit shows auth error
  ├── Empty message             → HTTP 422 → ChatKit shows validation error
  ├── MCP server fails to start → HTTP 503 → ChatKit shows service error
  ├── OPENAI_API_KEY missing    → HTTP 503 → ChatKit shows config error
  ├── Agent timeout (>30s)      → HTTP 504 → ChatKit shows timeout error
  └── Unexpected error          → HTTP 500 → ChatKit shows generic error

ChatKit frontend catches:
  ├── Network error (fetch fail) → ChatKit shows connection error
  ├── Stream interrupted         → ChatKit shows partial response
  └── 401 during stream          → Redirect to /login
```

### Auth Bridge — JWT in ChatKit

```
Frontend                         ChatKit Component              FastAPI
   │                                 │                             │
   │  User opens chat panel          │                             │
   │  ChatKit configured with:       │                             │
   │  api.url="/api/chatkit"         │                             │
   │  api.headers={Authorization}    │                             │
   │ ───────────────────────────────▶│                             │
   │                                 │  POST /api/chatkit          │
   │                                 │  Authorization: Bearer jwt  │
   │                                 │───────────────────────────▶│
   │                                 │                             │
   │                                 │                       get_current_user()
   │                                 │                       decode JWT → user_id
   │                                 │                             │
   │                                 │                       chatkit_server.process(
   │                                 │                         body,
   │                                 │                         context={"user_id": user_id}
   │                                 │                       )
   │                                 │                             │
   │                                 │  SSE stream with response  │
   │                                 │◀───────────────────────────│
   │  ChatKit renders response       │                             │
   │◀────────────────────────────────│                             │
```

**Critical security property**: The JWT token is passed via the ChatKit component's `api.headers` configuration. The FastAPI endpoint validates it using the same `get_current_user` dependency as all other endpoints. The ChatKit server's `respond()` method receives `user_id` via the `context` dict — never from the chat message content.

## Implementation Roadmap

### Step 1: Backend — Install ChatKit Python SDK

- Add `chatkit` to `backend/requirements.txt`
- Verify: `python -c "from chatkit.server import ChatKitServer; print('OK')"`
- No new environment variables needed (reuses `OPENAI_API_KEY` and `DATABASE_URL`)

### Step 2: Backend — Database-Backed ChatKit Store (FR-008)

Create `backend/src/chatkit/store.py`:
- Implement ChatKit `Store` abstract class using existing `Conversation` and `Message` models
- Map ChatKit "threads" to our `Conversation` model
- Map ChatKit "thread items" to our `Message` model
- Methods: `load_thread()`, `save_thread()`, `load_thread_items()`, `add_thread_item()`, `save_item()`, `delete_thread()`, `delete_thread_item()`
- Serialize/deserialize ChatKit types to our model fields
- Reuse `AsyncSessionLocal` for all DB operations

### Step 3: Backend — ChatKitServer Subclass (FR-003, FR-004, FR-005, FR-006)

Create `backend/src/chatkit/server.py`:
- Subclass `ChatKitServer` with `TodoChatKitServer`
- Implement `respond(thread, items, context)` method:
  1. Extract `user_id` from context
  2. Convert ChatKit thread items to agent input format
  3. Call existing `run_agent(user_id, input_items)` from `backend/src/agent/todo_agent.py`
  4. Convert `RunResult` to ChatKit `ThreadStreamEvent` objects
  5. Yield text events for the response
  6. Yield annotation events for tool calls (tool badges)
- Handle errors: `AgentTimeoutError` → timeout event, `AgentConnectionError` → error event
- Pass `store=DatabaseChatKitStore(...)` to server constructor

### Step 4: Backend — ChatKit Endpoint (FR-007)

Create `backend/src/api/chatkit_endpoint.py`:
```python
router = APIRouter(tags=["ChatKit"])

@router.post("/chatkit")
@limiter.limit("20/minute")
async def chatkit_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    body = await request.body()
    result = await chatkit_server.process(
        body,
        context={"user_id": current_user.id, "db": db}
    )
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```
- Register in `backend/src/main.py`
- Rate limit: 20/minute (matching existing chat endpoint)
- CORS: ensure `/api/chatkit` is allowed from frontend origin

### Step 5: Frontend — Install ChatKit React Package (FR-001)

- Run `npm install @openai/chatkit-react` in `frontend/`
- Add ChatKit script tag to `frontend/src/app/layout.tsx`:
  ```html
  <script src="https://cdn.openai.com/chatkit/latest/chatkit.bundle.js" async></script>
  ```
- Create `frontend/src/lib/chat-types.ts` with TypeScript types

### Step 6: Frontend — ChatContext and State Management (FR-008, FR-013)

Create `frontend/src/contexts/ChatContext.tsx`:
- State: `isOpen` (boolean), `conversationId` (string | null)
- Actions: `toggleChat()`, `openChat()`, `closeChat()`, `startNewChat()`
- `conversationId` persisted in localStorage for session continuity
- Provider wraps all authenticated pages

### Step 7: Frontend — Chat FAB Component (FR-001, FR-010)

Create `frontend/src/components/chat/ChatFAB.tsx`:
- Floating action button: fixed position, bottom-right, z-50
- Indigo-600 background (matching design system)
- Chat icon (from lucide-react: `MessageCircle`)
- onClick: toggle ChatContext.isOpen
- Only rendered when `isAuthenticated` is true (from AuthContext)
- Responsive: consistent size across mobile/desktop

### Step 8: Frontend — Chat Panel with ChatKit (FR-002, FR-003, FR-004, FR-005, FR-006, FR-010, FR-014, FR-015)

Create `frontend/src/components/chat/ChatPanel.tsx`:
- Renders when `ChatContext.isOpen` is true
- Desktop (>=768px): fixed-width panel (400px), bottom-right, above FAB
- Mobile (<768px): full-screen overlay with close button
- Embeds `<ChatKit>` component from `@openai/chatkit-react`:
  ```tsx
  <ChatKit
    api={{
      url: `${process.env.NEXT_PUBLIC_API_URL}/chatkit`,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }}
    theme="light"
    // ... additional config
  />
  ```
- ChatKit handles internally: message rendering, streaming, thinking indicator, auto-scroll, Enter/Shift+Enter, markdown
- Close button in header area

Create `frontend/src/components/chat/ChatLayout.tsx`:
- Auth-aware wrapper that renders ChatFAB + ChatPanel on authenticated pages
- Added to `layout.tsx` inside `<AuthProvider>`
- Conditionally rendered only when user is authenticated

### Step 9: Frontend — Layout Integration

Update `frontend/src/app/layout.tsx`:
- Import and render `<ChatLayout>` inside `<AuthProvider>`
- Add ChatKit script tag to `<head>`
- ChatLayout handles its own auth check — no changes needed in individual pages

### Step 10: Backend Tests

Create `backend/tests/test_chatkit_endpoint.py`:
- Test authenticated request → streaming response
- Test unauthenticated request → 401
- Test OPENAI_API_KEY missing → 503
- Test ChatKit server correctly invokes agent with user_id from JWT
- Test thread persistence across multiple requests

### Step 11: End-to-End Validation (SC-006)

Manual validation checklist:
1. Sign in via `/login`
2. Navigate to `/dashboard` → verify ChatFAB visible
3. Click FAB → verify chat panel opens
4. Send "Show me my tasks" → verify response with tool badge
5. Send "Add a task called 'Meeting prep'" → verify add_task badge
6. Send "Mark my grocery task as done" → verify complete_task badge
7. Send "Show me what's left" → verify list_tasks badge
8. Close panel → reopen → verify messages persist
9. Navigate to `/tasks` → verify new task visible, grocery marked done
10. Click "New Chat" → verify conversation reset

### Step 12: Submission Readiness Checklist

| Requirement | Phase | Status |
|-------------|-------|--------|
| Add tasks via web UI | Phase 2 | Verify |
| Delete tasks via web UI | Phase 2 | Verify |
| Update tasks via web UI | Phase 2 | Verify |
| View tasks via web UI | Phase 2 | Verify |
| Mark tasks complete via web UI | Phase 2 | Verify |
| MCP server with 5 tools | Phase 3.1 | Verify |
| Agent orchestrator with auth | Phase 3.2 | Verify |
| Chat endpoint with conversation persistence | Phase 3.2 | Verify |
| ChatKit UI with streaming | Phase 3.3 | Implement |
| Tool transparency badges | Phase 3.3 | Implement |
| Error handling in UI | Phase 3.3 | Implement |
| Responsive design (mobile + desktop) | Phase 3.3 | Implement |
| Multi-step natural language flow | Phase 3.3 | Validate |
| All tests passing | All | Verify |

## Key Architectural Decisions

| Decision | ADR | Summary |
|----------|-----|---------|
| Self-hosted ChatKit over OpenAI-hosted | **ADR-007** (new) | Self-hosted mode gives us control over auth, data, and agent logic; aligns with existing FastAPI backend |
| ChatKit streaming over custom SSE | **ADR-008** (new) | ChatKit SDK handles SSE protocol, event serialization, and client rendering; ~3x less code than custom implementation |
| localStorage for conversation_id | **ADR-009** (new) | conversation_id persisted in localStorage for session continuity; cleared on logout; simple and sufficient |
| Stdio transport (inherited) | [ADR-001](../../history/adr/001-mcp-transport-stdio.md) | MCP server spawned as subprocess; not modified |
| User ID passthrough (inherited) | [ADR-002](../../history/adr/002-auth-bridge-user-id-passthrough.md) | user_id from JWT injected into agent context |

## Dependencies (New)

| Package | Version | Purpose | Side |
|---------|---------|---------|------|
| `chatkit` | latest | ChatKit Python SDK for self-hosted server | Backend |
| `@openai/chatkit-react` | ^1.4.3 | React wrapper for ChatKit web component | Frontend |

## Environment Variables

No new environment variables. Existing variables:

| Variable | Required | Used By |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | Agents SDK (agent runs), ChatKit server |
| `DATABASE_URL` | Yes | ChatKit store (conversation persistence) |
| `BETTER_AUTH_SECRET` | Yes | JWT validation |
| `NEXT_PUBLIC_API_URL` | Yes | ChatKit api.url configuration |

## Risks

1. **ChatKit SDK compatibility with our database schema**: The ChatKit `Store` interface expects specific thread/item structures. Our `Conversation` and `Message` models may need adapter logic to map correctly. **Mitigation**: Implement a thin adapter layer in `DatabaseChatKitStore` that serializes/deserializes between ChatKit types and our SQLModel models. If the adaptation is too complex, fall back to letting ChatKit manage its own in-memory store and syncing to our DB separately.

2. **ChatKit web component styling conflicts with Tailwind**: The ChatKit `<openai-chatkit>` web component has its own CSS. It may conflict with or look inconsistent with our Tailwind-based design system. **Mitigation**: ChatKit supports theming via configuration (colors, density). We'll configure it to use our indigo-600 primary color and match our rounded/shadow patterns. The web component uses Shadow DOM, so conflicts should be minimal.

3. **ChatKit SDK may not expose tool call details in the stream**: If the ChatKit stream protocol doesn't surface `tool_calls` as distinct events, we can't show tool badges. **Mitigation**: The ChatKit SDK supports "annotations" and "source annotations" which can carry tool call metadata. If native support is insufficient, we can encode tool calls into the response text as formatted badges (e.g., inline markdown) or use ChatKit's custom widgets feature.

4. **JWT expiry during ChatKit streaming session**: If the JWT expires while the ChatKit component is maintaining a long-running session, subsequent requests will fail with 401. **Mitigation**: Configure the ChatKit component's `api.headers` to dynamically read the current token from localStorage on each request. Implement an error handler that detects 401 and triggers the AuthContext logout flow.

## Follow-ups

- **Phase IV**: Consider WebSocket/SSE for real-time task list updates after chat actions (currently requires manual refresh)
- **Phase IV**: Conversation list sidebar (view/switch between past conversations)
- **Phase IV**: ChatKit domain allowlist for production deployment
