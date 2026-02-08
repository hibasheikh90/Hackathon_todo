# Tasks: Phase 3 Part 3 — ChatKit UI and Final System Validation

**Feature**: OpenAI ChatKit UI and Final Validation
**Feature Branch**: `3-chatkit-ui-final-validation`
**Created**: 2026-02-08
**Status**: Pending
**Spec**: [specs/3-chatkit-ui-final-validation/spec.md](spec.md)
**Plan**: [specs/3-chatkit-ui-final-validation/plan.md](plan.md)

## Phase 1: Backend — ChatKit Python SDK Setup

### Goal
Install the ChatKit Python SDK and create the backend package scaffold for the self-hosted ChatKit server.

### Independent Test
`python -c "from chatkit.server import ChatKitServer; print('OK')"` succeeds. `backend/src/chatkit/__init__.py` exists.

### Implementation Tasks

- [ ] T001 Add `chatkit` to `backend/requirements.txt` and install it
  - **Precondition**: `backend/requirements.txt` exists
  - **Artifacts**: `backend/requirements.txt`
  - **Ref**: Plan Step 1

- [ ] T002 Create `backend/src/chatkit/__init__.py` with empty package init
  - **Precondition**: `backend/src/` directory exists
  - **Artifacts**: `backend/src/chatkit/__init__.py`
  - **Ref**: Plan Step 2, Project Structure

## Phase 2: Backend — Database-Backed ChatKit Store

### Goal
Implement the ChatKit `Store` adapter that maps ChatKit threads/items to our existing `Conversation` and `Message` database models.

### Independent Test
Create a `DatabaseChatKitStore` instance, call `save_thread()` with a ChatKit thread object, then `load_thread()` — verify the thread is returned with correct fields. Call `add_thread_item()` then `load_thread_items()` — verify items returned in order.

### Implementation Tasks

- [ ] T003 Implement `DatabaseChatKitStore` in `backend/src/chatkit/store.py` — Subclass the ChatKit `Store` abstract class. Map ChatKit "threads" to our `Conversation` model (thread.id → conversation.id, thread metadata → conversation fields). Map ChatKit "thread items" to our `Message` model (item.role → message.role, item.content → message.content, item.metadata → message.tool_calls). Implement required methods:
  - `load_thread(thread_id)` → Query `Conversation` by id, convert to ChatKit thread format
  - `save_thread(thread)` → Upsert `Conversation` record
  - `delete_thread(thread_id)` → Delete `Conversation` and cascade messages
  - `load_thread_items(thread_id)` → Query `Message` by conversation_id ordered by created_at, convert to ChatKit item format
  - `add_thread_item(thread_id, item)` → Insert `Message` record
  - `save_item(item)` → Update existing `Message` record
  - `load_item(item_id)` → Query single `Message` by id
  - `delete_thread_item(item_id)` → Delete single `Message` record
  - Use `AsyncSessionLocal` from existing database module for all DB operations
  - **Precondition**: T002, existing `Conversation` and `Message` models
  - **Artifacts**: `backend/src/chatkit/store.py`
  - **Ref**: Plan Step 2, FR-008, ADR-007

## Phase 3: Backend — ChatKit Server and Endpoint

### Goal
Create the ChatKitServer subclass that connects to our existing agent, and the FastAPI endpoint that serves it.

### Independent Test
`POST /api/chatkit` with valid JWT → returns SSE streaming response with agent output. Without JWT → HTTP 401. With missing `OPENAI_API_KEY` → HTTP 503.

### Implementation Tasks

- [ ] T004 Implement `TodoChatKitServer` in `backend/src/chatkit/server.py` — Subclass `ChatKitServer`. Constructor takes a `DatabaseChatKitStore` instance. Implement `respond(thread, items, context)` method:
  1. Extract `user_id` from `context["user_id"]`
  2. Convert ChatKit thread items to agent input format: `[{"role": item.role, "content": item.content}, ...]`
  3. Call `run_agent(user_id, input_items)` from `backend.src.agent.todo_agent`
  4. Extract `result.final_output` as response text
  5. Extract tool calls via `extract_tool_calls(result)`
  6. Yield `ThreadStreamEvent` for the response text
  7. Yield annotation events for each tool call (tool name + arguments)
  - Handle `AgentTimeoutError` → yield error event "AI response timed out"
  - Handle `AgentConnectionError` → yield error event "AI service temporarily unavailable"
  - Handle unexpected errors → log and yield generic error event
  - **Precondition**: T003, existing `run_agent()` and `extract_tool_calls()` from Part 2
  - **Artifacts**: `backend/src/chatkit/server.py`
  - **Ref**: Plan Step 3, FR-003, FR-004, FR-005, FR-006

- [ ] T005 Create `backend/src/api/chatkit_endpoint.py` — FastAPI router with `POST /api/chatkit` endpoint:
  - Auth: `Depends(get_current_user)` for JWT validation
  - Rate limit: `@limiter.limit("20/minute")`
  - Body: read raw request body via `await request.body()`
  - Instantiate or reuse `TodoChatKitServer` with `DatabaseChatKitStore`
  - Call `chatkit_server.process(body, context={"user_id": current_user.id})`
  - Return `StreamingResponse(result, media_type="text/event-stream")` for streaming results
  - Return `Response(content=result.json, media_type="application/json")` for non-streaming results
  - Validate `OPENAI_API_KEY` is configured → 503 if missing
  - **Precondition**: T004
  - **Artifacts**: `backend/src/api/chatkit_endpoint.py`
  - **Ref**: Plan Step 4, FR-007, FR-009, FR-011

- [ ] T006 Register the ChatKit router in `backend/src/main.py` — Import `chatkit_router` from `backend.src.api.chatkit_endpoint` and add `app.include_router(chatkit_router, prefix="/api")`. Ensure CORS middleware allows the ChatKit endpoint from the frontend origin.
  - **Precondition**: T005
  - **Artifacts**: `backend/src/main.py`
  - **Ref**: Plan Step 4

## Phase 4: Frontend — Dependencies and Types

### Goal
Install the ChatKit React package and create TypeScript type definitions for chat state.

### Independent Test
`npm ls @openai/chatkit-react` shows installed package. `frontend/src/lib/chat-types.ts` compiles without errors.

### Implementation Tasks

- [ ] T007 Install `@openai/chatkit-react` in the frontend — Run `npm install @openai/chatkit-react` in `frontend/`. Verify the package appears in `package.json` dependencies.
  - **Precondition**: `frontend/package.json` exists
  - **Artifacts**: `frontend/package.json`, `frontend/package-lock.json`
  - **Ref**: Plan Step 5

- [ ] T008 Create `frontend/src/lib/chat-types.ts` — Define TypeScript types for chat state:
  ```typescript
  export interface ToolCallInfo {
    tool: string;
    arguments: Record<string, unknown>;
  }

  export interface ChatState {
    isOpen: boolean;
    threadId: string | null;
  }
  ```
  - **Precondition**: T007
  - **Artifacts**: `frontend/src/lib/chat-types.ts`
  - **Ref**: Plan Step 5, Spec Key Entities

## Phase 5: Frontend — Chat Context and State Management

### Goal
Create the React context provider that manages chat panel open/close state and conversation (thread) ID persistence.

### Independent Test
Wrap a test component in `<ChatProvider>`, call `toggleChat()` — verify `isOpen` toggles. Call `startNewChat()` — verify `threadId` becomes null. Verify `threadId` is written to and read from localStorage.

### Implementation Tasks

- [ ] T009 Create `frontend/src/contexts/ChatContext.tsx` — React context with:
  - **State**: `isOpen` (boolean, default false), `threadId` (string | null, initialized from `localStorage.getItem('chatkit_thread_id')`)
  - **Actions**:
    - `toggleChat()` — toggle `isOpen`
    - `openChat()` — set `isOpen = true`
    - `closeChat()` — set `isOpen = false`
    - `startNewChat()` — set `threadId = null`, remove `chatkit_thread_id` from localStorage
    - `setThreadId(id: string)` — set `threadId`, persist to localStorage
  - **Persistence**: On `threadId` change, write to `localStorage.setItem('chatkit_thread_id', threadId)`. On mount, read from localStorage.
  - **Cleanup**: Export `useChat()` custom hook (like existing `useAuth()` pattern)
  - **Precondition**: T008
  - **Artifacts**: `frontend/src/contexts/ChatContext.tsx`
  - **Ref**: Plan Step 6, FR-008, FR-013, ADR-009

## Phase 6: Frontend — Chat UI Components

### Goal
Build the floating action button, chat panel with embedded ChatKit component, and the layout wrapper that ties them together.

### Independent Test
Navigate to `/dashboard` as an authenticated user → chat FAB visible in bottom-right. Click FAB → chat panel opens with ChatKit input area. Type a message and press Enter → message is sent to `/api/chatkit`. Close panel → reopen → ChatKit maintains conversation. On mobile viewport → panel fills screen.

### Implementation Tasks

- [ ] T010 Create `frontend/src/components/chat/ChatFAB.tsx` — Floating action button component:
  - Fixed position: `fixed bottom-6 right-6 z-50`
  - Styling: `w-14 h-14 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg`
  - Icon: `MessageCircle` from `lucide-react` (already installed)
  - onClick: `useChat().toggleChat()`
  - Transition: scale animation on hover
  - When chat is open, show X (close) icon instead of MessageCircle
  - Only renders when `useAuth().isAuthenticated` is true
  - **Precondition**: T009
  - **Artifacts**: `frontend/src/components/chat/ChatFAB.tsx`
  - **Ref**: Plan Step 7, FR-001, FR-010, SC-001

- [ ] T011 Create `frontend/src/components/chat/ChatPanel.tsx` — Chat panel component with embedded ChatKit:
  - Renders only when `useChat().isOpen` is true
  - **Desktop** (>=768px): `fixed bottom-24 right-6 w-[400px] h-[600px] z-40` — rounded-lg shadow-xl, positioned above FAB
  - **Mobile** (<768px): `fixed inset-0 z-40` — full screen overlay
  - **Header**: "AI Assistant" title, "New Chat" button (calls `startNewChat()`), close button (calls `closeChat()`)
  - **Body**: Embeds `<ChatKit>` component from `@openai/chatkit-react`:
    ```tsx
    <ChatKit
      api={{
        url: `${process.env.NEXT_PUBLIC_API_URL}/chatkit`,
        headers: () => ({
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
        }),
      }}
      theme={{
        primaryColor: '#4f46e5', // indigo-600
      }}
    />
    ```
  - ChatKit handles internally: message input, send button, thinking indicator, streaming, auto-scroll, markdown rendering, Enter/Shift+Enter
  - **Error handling**: Listen for ChatKit error events — on 401, display "Session expired" and link to login
  - **Precondition**: T010
  - **Artifacts**: `frontend/src/components/chat/ChatPanel.tsx`
  - **Ref**: Plan Step 8, FR-002 through FR-015, NFR-001 through NFR-004, SC-002, SC-003, SC-004, SC-007

- [ ] T012 Create `frontend/src/components/chat/ChatLayout.tsx` — Auth-aware wrapper component:
  - Uses `useAuth()` to check authentication
  - When `isAuthenticated`: renders `<ChatProvider>`, `<ChatFAB>`, and `<ChatPanel>`
  - When not authenticated: renders nothing (no FAB on login/signup pages)
  - This component is added to `layout.tsx` so it appears on all pages
  - **Precondition**: T011
  - **Artifacts**: `frontend/src/components/chat/ChatLayout.tsx`
  - **Ref**: Plan Step 8, Spec US1 Scenario 5

## Phase 7: Frontend — Layout Integration

### Goal
Wire the chat layout into the Next.js root layout so the FAB and panel appear on all authenticated pages.

### Independent Test
Navigate to `/dashboard` → FAB visible. Navigate to `/tasks` → FAB visible. Navigate to `/login` → FAB NOT visible. Click FAB on dashboard → panel opens. Navigate to `/tasks` with panel open → panel state preserved.

### Implementation Tasks

- [ ] T013 Update `frontend/src/app/layout.tsx` — Add ChatKit script tag and ChatLayout component:
  - Add `<Script src="https://cdn.openai.com/chatkit/latest/chatkit.bundle.js" strategy="afterInteractive" />` to the layout (import `Script` from `next/script`)
  - Import and render `<ChatLayout />` inside `<AuthProvider>`, after `{children}`
  - Do NOT modify `AuthProvider` or individual page components
  - **Precondition**: T012
  - **Artifacts**: `frontend/src/app/layout.tsx`
  - **Ref**: Plan Step 9, SC-008

## Phase 8: Backend — Integration Tests

### Goal
Validate the ChatKit endpoint with automated tests covering auth, streaming, and agent invocation.

### Independent Test
`pytest backend/tests/test_chatkit_endpoint.py` — all tests pass.

### Implementation Tasks

- [ ] T014 Create `backend/tests/test_chatkit_endpoint.py` — Integration tests for the ChatKit endpoint:
  - Test 1: Authenticated POST to `/api/chatkit` with valid body → returns response (200 or streaming)
  - Test 2: Unauthenticated POST to `/api/chatkit` → HTTP 401
  - Test 3: POST with missing `OPENAI_API_KEY` env → HTTP 503
  - Test 4: Verify the ChatKit server passes `user_id` from JWT to the agent (mock `run_agent`)
  - Test 5: Verify thread persistence — send two requests with same thread → second request has history context
  - Use the same test patterns as `test_chat_endpoint.py` (module aliasing for dual import paths, async fixtures, mock agent)
  - **Precondition**: T006
  - **Artifacts**: `backend/tests/test_chatkit_endpoint.py`
  - **Ref**: Plan Step 10, SC-001 through SC-005

## Phase 9: End-to-End Validation and Sign-off

### Goal
Execute the Phase 3 sign-off scenario through the ChatKit UI and verify all hackathon requirements are met.

### Independent Test
Manually execute the multi-step flow: "Add a meeting prep task, mark my grocery task as done, and show me what's left." Verify: (1) task created, (2) task completed, (3) remaining tasks listed, (4) UI shows tool badges, (5) task list page reflects changes.

### Implementation Tasks

- [ ] T015 Execute manual end-to-end validation — Follow the checklist from Plan Step 11:
  1. Sign in via `/login`
  2. Navigate to `/dashboard` → verify ChatFAB visible
  3. Click FAB → verify chat panel opens with ChatKit component
  4. Send "Show me my tasks" → verify streaming response with list_tasks tool activity
  5. Send "Add a task called 'Meeting prep'" → verify add_task tool activity
  6. Send "Mark my grocery task as done" → verify complete_task tool activity
  7. Send "Show me what's left" → verify list_tasks tool activity and correct remaining tasks
  8. Close panel → reopen → verify messages persist (ChatKit internal state)
  9. Navigate to `/tasks` → verify "Meeting prep" task visible, "Buy groceries" marked done
  10. Click "New Chat" → verify conversation reset
  - Document any failures and fix before sign-off
  - **Precondition**: T013, T014 (all implementation complete)
  - **Artifacts**: None (manual validation)
  - **Ref**: Plan Step 11, Spec US6, SC-006

- [ ] T016 Execute submission readiness checklist — Verify ALL hackathon requirements (Plan Step 12):
  - [ ] Phase 2: Add, delete, update, view, mark complete tasks via web UI
  - [ ] Phase 3.1: MCP server with 5 tools (21 tests passing)
  - [ ] Phase 3.2: Agent orchestrator with auth (34 tests passing)
  - [ ] Phase 3.3: ChatKit UI with streaming
  - [ ] Phase 3.3: Tool transparency (badges/annotations visible)
  - [ ] Phase 3.3: Error handling (401, 503, 504, network errors)
  - [ ] Phase 3.3: Responsive design (mobile + desktop)
  - [ ] All tests passing: `pytest backend/tests/` — 0 failures
  - [ ] No regression: existing task CRUD and auth still work
  - **Precondition**: T015
  - **Artifacts**: None (verification)
  - **Ref**: Plan Step 12, SC-008

## Dependencies

### Task Completion Order
1. T001-T002: Backend scaffold (parallel)
2. T003: ChatKit store (depends on T002)
3. T004: ChatKit server (depends on T003)
4. T005-T006: ChatKit endpoint + registration (sequential, depends on T004)
5. T007-T008: Frontend dependencies + types (parallel with backend, independent)
6. T009: Chat context (depends on T008)
7. T010: Chat FAB (depends on T009)
8. T011: Chat panel (depends on T010)
9. T012: Chat layout (depends on T011)
10. T013: Layout integration (depends on T012)
11. T014: Backend tests (depends on T006)
12. T015-T016: Validation (depends on T013 + T014)

### Critical Path
T001 → T003 → T004 → T005 → T006 → T014 (backend)
T007 → T009 → T010 → T011 → T012 → T013 (frontend)
T013 + T014 → T015 → T016 (validation)

### Parallel Execution
- **Backend and frontend are independent tracks** — T001-T006 (backend) and T007-T013 (frontend) can execute in parallel
- T001 and T002 can run in parallel (independent scaffold tasks)
- T007 and T008 can run in parallel (independent frontend setup)
- T014 (backend tests) can start as soon as T006 completes, independent of frontend work

## Success Criteria Mapping

| Success Criterion | Validated By |
|-------------------|-------------|
| SC-001: FAB visible, panel opens <100ms | T010, T011, T015 |
| SC-002: Optimistic messages + tool badges | T011, T015 |
| SC-003: Thinking indicator displayed | T011, T015 (built into ChatKit) |
| SC-004: Error states show user-friendly messages | T005, T011, T014, T015 |
| SC-005: Conversation persists across panel toggle | T009, T011, T015 |
| SC-006: Multi-step sign-off flow completes | T015 |
| SC-007: Responsive — mobile full-screen, desktop side panel | T011, T015 |
| SC-008: No regression on Phase 1/2 functionality | T016 |
