# ADR-009: localStorage for Client-Side Conversation ID Persistence

**Date**: 2026-02-08
**Status**: Accepted
**Context**: Phase 3 Part 3 — ChatKit UI and Final Validation

## Decision

Persist the current `conversation_id` (ChatKit thread ID) in **localStorage** so users can resume their conversation after closing the chat panel, navigating between pages, or refreshing the browser.

## Context

The spec requires "Conversation state persists across panel open/close and page navigation within a session" (SC-005). The backend already persists conversations in the database. The question is how the frontend remembers which conversation to resume.

## Options Considered

### Option A: localStorage (Selected)
- Store `chatkit_thread_id` in localStorage alongside the existing `auth_token`
- Clear on logout (alongside token) and on "New Chat" action
- **Pros**: Simple; survives page navigation and browser refresh; consistent with existing `auth_token` storage pattern; no new infrastructure.
- **Cons**: Persists beyond session (user might see stale conversation after days); shared across tabs.

### Option B: sessionStorage
- Store in sessionStorage (cleared when tab closes)
- **Pros**: Automatically cleared on tab close; per-tab isolation.
- **Cons**: Lost on browser refresh (sessionStorage survives refresh, but not tab close); different behavior from auth_token (which uses localStorage).

### Option C: React State Only
- Keep conversation_id in React context; no persistence
- **Pros**: Simplest implementation.
- **Cons**: Lost on page navigation (Next.js App Router re-renders); lost on refresh; violates SC-005.

### Option D: URL Parameter
- Store conversation_id in URL query parameter
- **Pros**: Shareable; bookmarkable.
- **Cons**: Clutters URLs; security concern (conversation IDs visible in browser history and logs); overcomplicates navigation.

## Rationale

1. localStorage is already used for `auth_token` in this project, establishing a precedent.
2. The ChatKit component may manage its own thread persistence internally, but we need a fallback to set the initial thread on mount.
3. Clearing on logout ensures users don't see stale conversations after re-authenticating as a different user.
4. The simplicity of localStorage matches the project's "smallest viable change" principle.

## Consequences

- The `ChatContext` provider MUST read `chatkit_thread_id` from localStorage on mount.
- The `ChatContext` MUST update localStorage when a new thread is created.
- The logout function MUST clear `chatkit_thread_id` alongside `auth_token`.
- The "New Chat" action MUST clear `chatkit_thread_id` from localStorage.
- If ChatKit internally manages thread IDs, we coordinate with its API to set/get the current thread.
