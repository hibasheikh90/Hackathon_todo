# Feature Specification: Phase 3 Part 3 — OpenAI ChatKit UI and Final Validation

**Feature Branch**: `3-chatkit-ui-final-validation`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase 3 Part 3: OpenAI ChatKit UI and Final Validation — Implement the conversational user interface using OpenAI ChatKit and perform final end-to-end validation of the AI-powered Todo system."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — User Opens the Chat Interface from Any Page (Priority: P1)

A logged-in user sees a floating chat button (FAB) on the dashboard and tasks pages. Clicking it opens a chat panel where they can type natural language messages to manage their tasks. The panel is responsive — full-width on mobile, a fixed-width drawer/popover on desktop.

**Why this priority**: This is the entry point for the entire Phase 3 AI experience. Without a visible, accessible chat UI, no other chat functionality can be accessed by end users.

**Independent Test**: Can be tested by loading the dashboard page as an authenticated user and verifying the chat FAB is visible, clickable, and opens a chat panel with an input field and message area.

**Acceptance Scenarios**:

1. **Given** a logged-in user on `/dashboard`, **When** they click the chat FAB, **Then** a chat panel opens with an empty message area, a text input, and a send button.
2. **Given** a logged-in user on `/tasks`, **When** they click the chat FAB, **Then** the same chat panel opens (consistent across pages).
3. **Given** a user on mobile (viewport < 768px), **When** they open the chat panel, **Then** it fills the full screen width with a close button to return to the underlying page.
4. **Given** a user on desktop (viewport >= 768px), **When** they open the chat panel, **Then** it appears as a fixed-width panel (400px) anchored to the bottom-right of the viewport.
5. **Given** an unauthenticated user, **When** they navigate to `/dashboard`, **Then** they are redirected to `/login` and the chat FAB is NOT rendered.

---

### User Story 2 — User Sends a Message and Receives a Streamed Response (Priority: P1)

A user types a natural language message (e.g., "Show me all my tasks") and presses Send (or Enter). The message appears immediately in the chat as a user bubble. An "Agent is thinking..." indicator appears while the backend processes the request. When the response arrives, it streams into the chat as an assistant bubble.

**Why this priority**: This is the core interaction loop — send message, see response. Without it, the chat UI is non-functional.

**Independent Test**: Can be tested by sending a message and verifying: (1) user message appears instantly, (2) a loading/thinking indicator shows, (3) the assistant response appears, (4) the thinking indicator disappears.

**Acceptance Scenarios**:

1. **Given** the chat panel is open, **When** the user types "Show me my tasks" and clicks Send, **Then** the message appears as a right-aligned user bubble immediately.
2. **Given** a message has been sent, **When** the backend is processing, **Then** an "Agent is thinking..." indicator (pulsing dots or spinner) is visible below the user's message.
3. **Given** the backend returns a response, **When** the response is received, **Then** it appears as a left-aligned assistant bubble and the thinking indicator disappears.
4. **Given** the backend returns tool_calls in the response, **When** the response is rendered, **Then** tool invocation badges (e.g., "Used: list_tasks") appear alongside or below the assistant's message.
5. **Given** the user presses Enter (without Shift), **When** the input field is focused, **Then** the message is sent (same as clicking Send).
6. **Given** the input field is empty, **When** the user clicks Send or presses Enter, **Then** nothing happens (no empty message sent).

---

### User Story 3 — Tool Invocation Badges Show MCP Tool Activity (Priority: P1)

When the agent uses MCP tools (e.g., `list_tasks`, `add_task`, `complete_task`), the UI shows visual badges or pills indicating which tools were called. This provides transparency into what the AI did behind the scenes.

**Why this priority**: Tool transparency is a core UX requirement from the hackathon rubric. Users must understand what actions the AI took on their behalf.

**Independent Test**: Can be tested by sending a message that triggers a tool call (e.g., "Add a task called 'Test'") and verifying that a badge like "add_task" appears in the response area.

**Acceptance Scenarios**:

1. **Given** the agent calls `add_task` in response to "Add a task to buy milk", **When** the response is rendered, **Then** a badge reading "add_task" is shown with the assistant message.
2. **Given** the agent calls multiple tools (e.g., `list_tasks` then `complete_task`), **When** the response is rendered, **Then** multiple badges appear, one per tool call.
3. **Given** the agent responds without using any tools (e.g., clarification question), **When** the response is rendered, **Then** no tool badges appear.
4. **Given** a tool badge is displayed, **When** hovered/tapped, **Then** it optionally shows a tooltip with the tool arguments (e.g., `{title: "Buy milk"}`).

---

### User Story 4 — Conversation Persists Across Panel Open/Close (Priority: P1)

A user can close the chat panel and reopen it without losing their conversation. The conversation state is maintained client-side within the session and backed by the database on the server.

**Why this priority**: Users will frequently toggle the chat panel while navigating. Losing context on each toggle would be frustrating and break the multi-turn capability.

**Independent Test**: Can be tested by sending a message, closing the panel, reopening it, and verifying the previous messages are still visible.

**Acceptance Scenarios**:

1. **Given** a user has sent 3 messages in a conversation, **When** they close and reopen the chat panel, **Then** all 3 messages (user + assistant) are visible in the same order.
2. **Given** a user has an active conversation_id, **When** they send a new message after reopening, **Then** the backend receives the same conversation_id (maintaining context).
3. **Given** a user navigates from `/dashboard` to `/tasks`, **When** the chat panel is reopened, **Then** the conversation state is preserved (same messages, same conversation_id).

---

### User Story 5 — Error States are Clearly Communicated (Priority: P1)

When errors occur (network failure, auth expiry, agent timeout, service unavailable), the chat UI shows clear, user-friendly error messages — not raw HTTP errors or blank states.

**Why this priority**: Error handling is critical for a production-quality demo. Unclear errors will confuse users and judges.

**Independent Test**: Can be tested by simulating error conditions (disconnect network, use expired token) and verifying appropriate error messages appear in the chat.

**Acceptance Scenarios**:

1. **Given** the backend returns HTTP 401 (expired token), **When** the error is received, **Then** an error message appears: "Your session has expired. Please log in again." with a link/button to the login page.
2. **Given** the backend returns HTTP 503 (AI service unavailable), **When** the error is received, **Then** an error message appears: "AI assistant is temporarily unavailable. Please try again later."
3. **Given** the backend returns HTTP 504 (agent timeout), **When** the error is received, **Then** an error message appears: "The AI took too long to respond. Please try a simpler request."
4. **Given** a network error occurs (fetch fails), **When** the error is caught, **Then** an error message appears: "Connection lost. Please check your internet and try again."
5. **Given** an error message is displayed, **When** the user sends a new message, **Then** the error message remains visible but the new message is sent normally.

---

### User Story 6 — Final End-to-End Validation Flow (Priority: P1)

A user executes a complex multi-step natural language flow through the chat: "Add a meeting prep task for tomorrow, mark my grocery task as done, and show me what's left." The system successfully creates a task, completes another, lists remaining tasks, and confirms all actions in a coherent response.

**Why this priority**: This is the Phase 3 sign-off scenario. It validates the entire stack: ChatKit UI → Chat Endpoint → Agent → MCP Tools → Database → Response → UI render.

**Independent Test**: Can be tested end-to-end by running the full flow and verifying: (1) the task is created, (2) the grocery task is marked complete, (3) the remaining tasks are listed, (4) the response is coherent, (5) tool badges show all 3 tool calls.

**Acceptance Scenarios**:

1. **Given** the user has a task "Buy groceries" (pending), **When** they send "Add a meeting prep task, mark my grocery task as done, and show me what's left", **Then** the agent calls `add_task`, `complete_task`, and `list_tasks` in sequence.
2. **Given** the multi-step flow completes, **When** the response is rendered, **Then** the assistant message confirms all three actions in natural language.
3. **Given** the multi-step flow completes, **When** the response is rendered, **Then** tool badges show "add_task", "complete_task", and "list_tasks".
4. **Given** the user navigates to `/tasks` after the flow, **When** the task list loads, **Then** the new "Meeting prep" task is visible and "Buy groceries" is marked complete — confirming the AI actions persisted to the database.

---

### User Story 7 — New Conversation Can Be Started (Priority: P2)

A user can start a fresh conversation by clicking a "New Chat" button, which clears the current chat history and begins a new conversation with a new `conversation_id`.

**Why this priority**: While the system works with a single ongoing conversation, the ability to start fresh is important for usability when the context becomes stale.

**Independent Test**: Can be tested by starting a conversation, clicking "New Chat", and verifying the messages are cleared and a new conversation_id is generated on the next message.

**Acceptance Scenarios**:

1. **Given** a user has an active conversation with messages, **When** they click "New Chat", **Then** the message area is cleared.
2. **Given** the user starts typing after clicking "New Chat", **When** the first message is sent, **Then** a new `conversation_id` is returned by the backend.
3. **Given** the user started a new chat, **When** they send a message referencing old context (e.g., "mark the first one done"), **Then** the agent does not have access to the old conversation's context and asks for clarification.

---

### Edge Cases

- What happens when the user sends a message while a previous request is still in flight? The UI MUST disable the Send button and input field until the current response is received, preventing duplicate requests.
- What happens when the chat panel is open and the JWT token expires mid-conversation? The next request MUST detect the 401, show an auth error message, and offer a path to re-login.
- What happens when the response contains markdown formatting (bold, lists, code blocks)? The assistant message MUST render markdown properly using a markdown renderer.
- What happens when the user sends a very long message (>5000 characters)? The UI SHOULD truncate or warn, and the backend validation catches it.
- What happens when the chat history becomes very long (100+ messages)? The UI MUST auto-scroll to the latest message and perform well (no lag).
- What happens when the user refreshes the browser? The conversation_id SHOULD be persisted in localStorage so the user can resume their last conversation.
- What happens if the user rapidly clicks the chat FAB? The panel MUST toggle cleanly without visual glitches or state corruption.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render a floating action button (FAB) on all authenticated pages (`/dashboard`, `/tasks`) that opens a chat panel when clicked.
- **FR-002**: The chat panel MUST include a message display area (scrollable), a text input field, and a Send button.
- **FR-003**: User messages MUST appear immediately in the chat (optimistic rendering) as right-aligned bubbles before the backend responds.
- **FR-004**: An "Agent is thinking..." indicator MUST be displayed while awaiting a backend response.
- **FR-005**: Assistant responses MUST be rendered as left-aligned bubbles with support for basic markdown (bold, italic, lists, code).
- **FR-006**: Tool invocation badges MUST be displayed alongside assistant messages when `tool_calls` are present in the response.
- **FR-007**: The chat panel MUST send messages to `POST /api/chat` with the authenticated user's JWT token and the current `conversation_id`.
- **FR-008**: The `conversation_id` MUST be stored in component state (and optionally localStorage) to maintain conversation continuity across panel open/close cycles and page navigation.
- **FR-009**: Error responses (401, 503, 504, network errors) MUST be displayed as distinct error messages in the chat with user-friendly text.
- **FR-010**: The chat panel MUST be responsive — full-screen on mobile (< 768px), fixed-width side panel on desktop (>= 768px).
- **FR-011**: The Send button and input MUST be disabled while a request is in flight to prevent duplicate sends.
- **FR-012**: The message area MUST auto-scroll to the latest message when a new message is added.
- **FR-013**: A "New Chat" button MUST be provided to clear the current conversation and start fresh.
- **FR-014**: Pressing Enter (without Shift) MUST send the message. Shift+Enter MUST insert a newline.
- **FR-015**: The chat panel MUST render markdown in assistant messages using a lightweight markdown renderer.

### Non-Functional Requirements

- **NFR-001**: The chat panel MUST open/close in under 100ms (no perceptible delay).
- **NFR-002**: The UI MUST remain responsive with 100+ messages in the chat history (virtual scrolling or pagination if needed).
- **NFR-003**: The chat FAB and panel MUST not interfere with the existing task list UI or navigation.
- **NFR-004**: All chat UI components MUST follow the existing Tailwind CSS design system (indigo-600 primary, gray-50 bg, rounded-lg cards).
- **NFR-005**: The chat UI MUST work on all modern browsers (Chrome, Firefox, Safari, Edge).

### Key Entities

- **ChatMessage** (frontend-only state): `id` (string, client-generated), `role` ("user" | "assistant" | "error"), `content` (string), `toolCalls` (array, optional), `timestamp` (Date), `isLoading` (boolean, for thinking state).
- **Conversation** (existing backend model, unchanged): `id`, `user_id`, `created_at`, `updated_at`.
- **Message** (existing backend model, unchanged): `id`, `conversation_id`, `role`, `content`, `tool_calls`, `created_at`.
- **ChatResponse** (existing backend response): `conversation_id`, `response`, `tool_calls[]`.

### Integration Points

- **Backend Chat Endpoint**: `POST /api/chat` with `{"message": string, "conversation_id": string | null}`. Response: `{"conversation_id": string, "response": string, "tool_calls": [{tool: string, arguments: object}]}`.
- **Authentication**: Uses existing `AuthContext` and JWT token from `localStorage`. The `apiClient` singleton automatically attaches the `Authorization: Bearer <token>` header.
- **API Client**: Uses existing `apiClient` from `frontend/src/lib/api.ts` for all requests.
- **Routing**: Chat FAB is rendered in the authenticated layout, not on individual pages, to ensure consistency.
- **Task List Sync**: After chat interactions that modify tasks (add, complete, delete, update), the task list on `/tasks` MUST reflect changes on next load (no real-time sync required — standard fetch on page load is sufficient).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chat FAB is visible on all authenticated pages and opens a functional chat panel in under 100ms.
- **SC-002**: User messages appear instantly (optimistic rendering) and assistant responses appear with tool badges when applicable.
- **SC-003**: The "Agent is thinking..." indicator is displayed for every pending request and disappears when the response arrives.
- **SC-004**: Error states (401, 503, 504, network errors) show user-friendly messages instead of raw errors.
- **SC-005**: Conversation state persists across panel open/close and page navigation within a session.
- **SC-006**: The multi-step sign-off flow ("Add a meeting prep task, mark grocery as done, show what's left") completes successfully with correct tool badges.
- **SC-007**: The chat panel is responsive — full-screen mobile, side panel desktop.
- **SC-008**: All existing Phase 1 and Phase 2 functionality (task CRUD via web UI, authentication) continues to work without regression.

### File Structure (Expected Output)

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                    # Updated: include ChatProvider + ChatFAB
│   │   ├── dashboard/page.tsx            # Existing (unchanged)
│   │   └── tasks/page.tsx                # Existing (unchanged)
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatFAB.tsx              # NEW: Floating action button
│   │   │   ├── ChatPanel.tsx            # NEW: Main chat panel container
│   │   │   ├── ChatMessages.tsx         # NEW: Message list with auto-scroll
│   │   │   ├── ChatMessage.tsx          # NEW: Individual message bubble
│   │   │   ├── ChatInput.tsx            # NEW: Text input + send button
│   │   │   ├── ToolBadge.tsx            # NEW: Tool invocation badge/pill
│   │   │   └── ThinkingIndicator.tsx    # NEW: Pulsing dots indicator
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx             # Existing (unchanged)
│   │   │   ├── TaskItem.tsx             # Existing (unchanged)
│   │   │   └── CreateTaskForm.tsx       # Existing (unchanged)
│   │   ├── ErrorBoundary.tsx            # Existing (unchanged)
│   │   └── UserFriendlyError.tsx        # Existing (unchanged)
│   ├── contexts/
│   │   ├── AuthContext.tsx              # Existing (unchanged)
│   │   └── ChatContext.tsx              # NEW: Chat state management
│   └── lib/
│       ├── api.ts                       # Existing (unchanged)
│       ├── validation.ts               # Existing (unchanged)
│       └── chat-types.ts               # NEW: TypeScript types for chat
specs/
└── 3-chatkit-ui-final-validation/
    ├── spec.md                          # THIS FILE
    ├── plan.md                          # Architecture plan (next step)
    └── tasks.md                         # Implementation tasks (after plan)
```

### Constitution Compliance Check

| Principle | Compliance |
|-----------|------------|
| I. Spec-Driven Development | This spec precedes all implementation |
| II. AI-Native Development | Implementation via Claude Code |
| III. Reusable Intelligence | Chat components are modular and reusable |
| IV. Full-Stack Integration | ChatKit UI integrates with existing Next.js + FastAPI stack |
| V. Security-First | JWT auth enforced for all chat requests via existing AuthContext |
| VI. Cloud-Native | Stateless UI; all state in database via backend |
| VII. MCP-First | UI displays MCP tool badges; all task ops via MCP |
| VIII. Stateless Chat | Server-side stateless; client state is ephemeral cache |
| IX. AI Agent Behavior | Tool transparency via badges; error clarity via error states |
