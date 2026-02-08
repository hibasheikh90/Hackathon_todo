# ADR-008: ChatKit Streaming Protocol over Custom SSE/WebSocket

**Date**: 2026-02-08
**Status**: Accepted
**Context**: Phase 3 Part 3 — ChatKit UI and Final Validation

## Decision

Use the **ChatKit SDK's built-in SSE streaming protocol** for real-time response delivery, rather than implementing a custom SSE or WebSocket solution.

## Context

The spec requires "Real-time Streaming: Messages from the agent stream in real-time rather than waiting for the full response." There are multiple ways to achieve this:

1. ChatKit's built-in streaming (SSE via `ChatKitServer`)
2. Custom SSE endpoint with manual `text/event-stream` implementation
3. WebSocket connection for bidirectional streaming

## Options Considered

### Option A: ChatKit Built-in Streaming (Selected)
- `ChatKitServer.process()` returns a `StreamingResult` that FastAPI wraps in `StreamingResponse`
- The `respond()` method yields `ThreadStreamEvent` objects incrementally
- The `<ChatKit>` React component handles client-side stream parsing automatically
- **Pros**: Zero streaming code to write; protocol compatibility guaranteed between SDK server and client; handles backpressure, reconnection, and partial rendering; ChatKit component renders streaming text with built-in "thinking" indicator.
- **Cons**: Tied to ChatKit's event format; less control over individual stream events.

### Option B: Custom SSE
- Build a `text/event-stream` endpoint from scratch
- Frontend uses `EventSource` or `fetch` with readable stream
- **Pros**: Full control over event format and timing.
- **Cons**: ~200 lines of streaming code; must handle content-type, event serialization, error events, reconnection; must build client-side stream parser; must implement thinking indicator, auto-scroll, and incremental rendering manually.

### Option C: WebSocket
- Bidirectional WebSocket connection for chat
- **Pros**: Bidirectional; lower overhead for frequent messages.
- **Cons**: Requires WebSocket support in deployment (may not work behind all proxies); significantly more complex connection lifecycle; ChatKit doesn't support WebSocket as a transport; most over-engineered option for request-response chat.

## Rationale

1. ChatKit's streaming is purpose-built for exactly this use case — chat with AI agents.
2. The `respond()` method yields events naturally, matching our agent's output lifecycle.
3. The ChatKit React component handles all client-side streaming UX (thinking indicator, incremental text, auto-scroll).
4. We avoid ~200+ lines of custom streaming infrastructure.
5. SSE (used by ChatKit) works through standard HTTP proxies and load balancers.

## Consequences

- The ChatKit endpoint MUST return `StreamingResponse` with `text/event-stream` media type when `ChatKitServer.process()` returns a `StreamingResult`.
- The `respond()` method MUST yield `ThreadStreamEvent` objects to stream response text incrementally.
- Tool call information MUST be encoded as ChatKit annotations within the stream.
- The frontend MUST NOT implement custom stream parsing — it relies on the `<ChatKit>` component.
- If ChatKit's streaming doesn't support a feature we need (e.g., custom tool badges), we can enhance the response text with inline formatting (markdown) as a fallback.
