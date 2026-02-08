# ADR-007: Self-Hosted ChatKit over OpenAI-Hosted

**Date**: 2026-02-08
**Status**: Accepted
**Context**: Phase 3 Part 3 — ChatKit UI and Final Validation

## Decision

Use **self-hosted ChatKit** mode with the ChatKit Python SDK (`chatkit` package) running on our FastAPI backend, rather than the OpenAI-hosted ChatKit service.

## Context

OpenAI ChatKit offers two deployment modes:
1. **OpenAI-Hosted**: Fastest setup. OpenAI handles infrastructure, storage, and inference. Requires configuring agents in OpenAI's Agent Builder dashboard.
2. **Self-Hosted**: Maximum control. You run a `ChatKitServer` on your own infrastructure using the ChatKit Python SDK. Full control over data, auth, and agent logic.

Our system already has a complete backend: FastAPI with JWT auth, OpenAI Agents SDK agent, MCP server, and database-backed conversation persistence. The question is whether to point ChatKit at OpenAI's hosted service or integrate it with our existing backend.

## Options Considered

### Option A: Self-Hosted ChatKit (Selected)
- Run `ChatKitServer` subclass in our FastAPI process
- ChatKit React component configured with `api.url="/api/chatkit"`
- Our server handles auth, agent invocation, and persistence
- **Pros**: Uses existing JWT auth, agent, and database; no data leaves our infrastructure; full control over agent behavior (P+Q+P stance); no additional OpenAI service dependency beyond the API key we already use; conversation data stays in our Neon DB.
- **Cons**: Must implement `ChatKitServer` subclass and `Store` adapter; slightly more backend code.

### Option B: OpenAI-Hosted ChatKit
- Configure ChatKit to use OpenAI's hosted backend
- Create agents in OpenAI's Agent Builder
- **Pros**: Zero backend code; instant setup.
- **Cons**: Cannot use our existing JWT auth system (OpenAI uses its own session tokens); cannot use our existing MCP server or Agents SDK agent; conversation data stored on OpenAI's servers, not in our Neon DB; would need to recreate the entire agent + tool setup in Agent Builder; breaks constitution principles V (security-first with our auth), VII (MCP-first), and VIII (database-backed persistence).

## Rationale

1. We already have a fully functional agent (P+Q+P stance, MCP tools, user_id injection) that must be reused, not duplicated.
2. Our JWT auth system (Better Auth) is the security boundary — ChatKit must integrate with it, not replace it.
3. Constitution Principle VIII mandates database-backed persistence in our Neon instance.
4. Self-hosted mode is explicitly designed for this use case: "maximum control over workflows and data handling."
5. The ChatKit Python SDK provides `ChatKitServer` as a clean abstraction — we only need to implement `respond()` and a `Store`.

## Consequences

- The backend MUST implement a `ChatKitServer` subclass with a `respond()` method that calls our existing `run_agent()`.
- The backend MUST implement a `Store` subclass that maps ChatKit threads/items to our `Conversation` and `Message` models.
- The frontend ChatKit component MUST be configured with `api.url` pointing to our FastAPI endpoint and `api.headers` including the JWT token.
- The existing `POST /api/chat` endpoint is preserved for backward compatibility and direct API testing.
