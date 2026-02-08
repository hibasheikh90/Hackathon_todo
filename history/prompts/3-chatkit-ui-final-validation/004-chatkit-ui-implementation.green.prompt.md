---
id: 004
title: ChatKit UI Full Implementation
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 3-chatkit-ui-final-validation
branch: main
user: hayas
command: /sp.implement
labels: ["chatkit", "openai", "frontend", "backend", "integration-tests"]
links:
  spec: specs/3-chatkit-ui-final-validation/spec.md
  ticket: null
  adr: history/adr/007-self-hosted-chatkit.md, history/adr/008-chatkit-streaming-protocol.md, history/adr/009-localstorage-conversation-persistence.md
  pr: null
files:
  - backend/src/chatkit/__init__.py
  - backend/src/chatkit/store.py
  - backend/src/chatkit/server.py
  - backend/src/api/chatkit_endpoint.py
  - backend/src/main.py
  - backend/requirements.txt
  - backend/tests/test_chatkit_endpoint.py
  - frontend/src/lib/chat-types.ts
  - frontend/src/contexts/ChatContext.tsx
  - frontend/src/components/chat/ChatFAB.tsx
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/ChatLayout.tsx
  - frontend/src/app/layout.tsx
  - frontend/package.json
tests:
  - tests/test_chatkit_endpoint.py::TestChatKitAuth::test_no_auth_returns_401
  - tests/test_chatkit_endpoint.py::TestChatKitAuth::test_invalid_token_returns_401
  - tests/test_chatkit_endpoint.py::TestChatKitAuth::test_expired_token_returns_401
  - tests/test_chatkit_endpoint.py::TestChatKitAPIKey::test_missing_api_key_returns_503
  - tests/test_chatkit_endpoint.py::TestChatKitAPIKey::test_placeholder_api_key_returns_503
  - tests/test_chatkit_endpoint.py::TestChatKitUserIdInjection::test_server_passes_user_id_to_agent
---

## Prompt

/sp.implement

## Response snapshot

Implemented Phase 3 Part 3: OpenAI ChatKit UI and Final Validation across 16 tasks (T001-T016) in 9 phases.

**Backend (5 new files, 2 modified):**
- `DatabaseChatKitStore` — Maps ChatKit threads/items to existing Conversation/Message DB models with pagination support
- `TodoChatKitServer` — ChatKitServer subclass delegating to existing run_agent() with error handling for timeout/connection/unexpected errors
- `POST /api/chatkit` endpoint — JWT-authenticated, rate-limited (20/min), OPENAI_API_KEY validation, StreamingResponse for SSE
- 6 integration tests — auth (3), API key validation (2), user ID injection (1)

**Frontend (5 new files, 2 modified):**
- `ChatContext` — React context managing isOpen, threadId state with localStorage persistence
- `ChatFAB` — Floating action button (bottom-right, indigo, MessageCircle/X icons)
- `ChatPanel` — useChatKit hook with custom fetch for JWT injection, mobile overlay + desktop side panel
- `ChatLayout` — Auth-aware wrapper rendering chat components only when authenticated
- Layout integration — ChatKit bundle script, ChatLayout in root layout

**Validation Results:**
- 38 backend tests passing (21 MCP + 11 Chat + 6 ChatKit)
- TypeScript compilation: clean
- Next.js build: clean (all 9 pages generated)

## Outcome

- ✅ Impact: Complete ChatKit UI integration — self-hosted backend with agent delegation, responsive frontend with streaming chat
- 🧪 Tests: 6/6 ChatKit tests passing, 38/38 total backend tests passing
- 📁 Files: 10 new files created, 4 files modified
- 🔁 Next prompts: E2E manual testing with real OPENAI_API_KEY, production deployment validation
- 🧠 Reflection: ChatKit SDK pydantic types are strict (literal types like 'output_text' not 'text', 'input_text' not 'text'; required InferenceOptions on UserMessageItem; ThreadStatus is a model not a string). Must introspect SDK types before constructing objects.

## Evaluation notes (flywheel)

- Failure modes observed: ChatKit SDK type mismatches (type literals, required fields) caused test failures that revealed bugs in server.py AssistantMessageContent construction
- Graders run and results (PASS/FAIL): pytest PASS, tsc PASS, next build PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add error boundary around ChatKit component for graceful degradation
