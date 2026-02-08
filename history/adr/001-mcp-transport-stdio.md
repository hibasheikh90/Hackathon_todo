# ADR-001: MCP Transport — Stdio over HTTP/SSE

**Date**: 2026-02-07
**Status**: Accepted
**Context**: Phase 3 Part 1 — MCP Server and Tooling

## Decision

Use **stdio transport** for the MCP server. The server runs as a subprocess spawned by the OpenAI Agents SDK via `MCPServerStdio`.

## Context

The MCP protocol supports multiple transports:
1. **Stdio**: Server communicates via stdin/stdout JSON-RPC. Client spawns server as subprocess.
2. **Streamable HTTP**: Server runs as HTTP endpoint. Client connects via HTTP requests.
3. **SSE (legacy)**: Server-Sent Events transport. Deprecated.

The MCP server needs to be callable from the OpenAI Agents SDK (Phase 3 Part 2) and testable with MCP Inspector.

## Options Considered

### Option A: Stdio (Selected)
- **Pros**: Simplest setup; native `MCPServerStdio` support in OpenAI Agents SDK; no port management; no CORS; MCP Inspector compatible; no authentication needed (subprocess isolation); works locally and in containers.
- **Cons**: Cannot be called from external network clients; one connection per subprocess instance.

### Option B: Streamable HTTP
- **Pros**: Network-accessible; multiple clients can connect; supports horizontal scaling.
- **Cons**: Requires port allocation; needs CORS configuration; needs its own authentication layer; more complex deployment; OpenAI Agents SDK `MCPServerStdio` is the primary integration path.

### Option C: SSE (Legacy)
- **Pros**: None (deprecated).
- **Cons**: Deprecated upstream; will be removed.

## Rationale

1. The OpenAI Agents SDK's `MCPServerStdio` spawns the MCP server as a subprocess, naturally using stdio.
2. The MCP server is NOT a public-facing service — it's an internal tool provider for the AI agent.
3. Subprocess isolation provides security: no network attack surface, no auth needed at MCP level.
4. Stdio is the standard transport for MCP Inspector testing.
5. If network access is needed in Phase IV/V (Kubernetes), this can be revisited as a separate ADR.

## Consequences

- The MCP server MUST be runnable as `python -m backend.src.mcp.server`.
- Tools MUST NOT write to stdout (corrupts JSON-RPC). Use `logging` to stderr.
- Each agent instance spawns its own MCP server subprocess.
- The FastAPI chat endpoint manages subprocess lifecycle via `MCPServerStdio` context manager.
