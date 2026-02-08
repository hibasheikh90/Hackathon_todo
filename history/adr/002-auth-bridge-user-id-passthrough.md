# ADR-002: Authentication Bridge — User ID Passthrough

**Date**: 2026-02-07
**Status**: Accepted
**Context**: Phase 3 Part 1 — MCP Server and Tooling

## Decision

The MCP server does NOT validate JWTs. Authentication is enforced at the FastAPI chat endpoint layer. The `user_id` is passed as an explicit parameter to every MCP tool call. The MCP server trusts this parameter because it runs as a subprocess of the authenticated FastAPI process.

## Context

Phase 2 uses Better Auth with JWT tokens. Every REST API endpoint validates the JWT and extracts `user_id`. In Phase 3, the AI agent (OpenAI Agents SDK) calls MCP tools instead of REST endpoints. The question is: where does JWT validation happen?

## Architecture

```
User → [JWT] → FastAPI Chat Endpoint → [validates JWT, extracts user_id]
                    ↓
             OpenAI Agents SDK → [passes user_id in tool params]
                    ↓
             MCP Server (stdio) → [trusts user_id, queries DB]
                    ↓
             Neon PostgreSQL → [WHERE user_id = ? enforces isolation]
```

## Options Considered

### Option A: User ID Passthrough (Selected)
- JWT validation happens ONCE at the FastAPI chat endpoint.
- `user_id` is injected into every MCP tool call by the agent's system prompt or by the chat endpoint wrapper.
- MCP tools use `user_id` in all DB queries (WHERE clause).
- **Pros**: Simple; no JWT dependency in MCP server; single point of auth; reuses Phase 2 auth middleware.
- **Cons**: MCP server trusts caller — must not be exposed externally.

### Option B: JWT Validation Inside MCP Tools
- Each MCP tool receives a JWT token as parameter, validates it, extracts user_id.
- **Pros**: Defense in depth; MCP server is self-securing.
- **Cons**: Requires `python-jose` + `BETTER_AUTH_SECRET` in MCP process; adds ~50ms per tool call for JWT decode; duplicates auth logic; MCP server is a subprocess (not externally accessible) so the threat model doesn't justify it.

### Option C: Shared Session Token
- FastAPI creates a short-lived session token after JWT validation, passes it to MCP server.
- **Pros**: Time-limited trust.
- **Cons**: Requires session store; over-engineered for subprocess communication.

## Rationale

1. The MCP server runs as a subprocess — only the FastAPI process can communicate with it.
2. There is no network path for external clients to reach the MCP server directly.
3. User isolation is enforced at the SQL level (`WHERE user_id = ?`) regardless of the auth mechanism.
4. The chat endpoint already validates JWT (reusing Phase 2 auth middleware). Adding JWT validation in MCP tools would be redundant.
5. This pattern follows the hackathon architecture diagram where the chat endpoint is the security boundary.

## Consequences

- Every MCP tool MUST accept `user_id` as a required string parameter.
- Every database query in MCP tools MUST filter by `user_id`.
- The MCP server MUST NOT be exposed as a network service (stdio only).
- The FastAPI chat endpoint MUST validate JWT before invoking the agent.
- If the MCP server transport changes to HTTP in Phase IV/V, this ADR MUST be revisited to add authentication.
