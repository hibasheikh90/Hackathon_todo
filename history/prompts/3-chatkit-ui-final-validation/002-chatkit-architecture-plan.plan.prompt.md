---
id: 002
title: ChatKit UI Architecture Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 3-chatkit-ui-final-validation
branch: 3-chatkit-ui-final-validation
user: hayas
command: /sp.plan
labels: ["chatkit", "architecture", "streaming", "self-hosted", "phase3-part3"]
links:
  spec: specs/3-chatkit-ui-final-validation/spec.md
  ticket: null
  adr: history/adr/007-self-hosted-chatkit.md, history/adr/008-chatkit-streaming-protocol.md, history/adr/009-localstorage-conversation-persistence.md
  pr: null
files:
  - specs/3-chatkit-ui-final-validation/plan.md
  - history/adr/007-self-hosted-chatkit.md
  - history/adr/008-chatkit-streaming-protocol.md
  - history/adr/009-localstorage-conversation-persistence.md
tests:
  - none (plan phase)
---

## Prompt

/sp.plan "Phase 3 Part 3: ChatKit UI and Final System Validation Architecture"

Instructions:
1. Review the Phase 3 Part 2 Agent logic and the existing Phase 2 Next.js frontend.
2. Generate Architectural Decision Records (ADRs) for:
   - Streaming Implementation: How to handle real-time response streaming between the Agent and the ChatKit UI.
   - Agent Feedback Loop: UI patterns for displaying tool execution status to the user.
   - State Persistence: Deciding if/how chat history is persisted across page refreshes using local storage or backend sessions.
3. Create a multi-step roadmap including:
   - Integrating OpenAI ChatKit components into the Next.js layout.
   - Connecting the frontend message handler to the Part 2 Agent orchestrator.
   - Implementing a "Submission Readiness" checklist to verify all Phase 3 requirements.

Focus on:
- Responsive Design: Ensure the chat interface is usable across desktop and mobile.
- Error Boundaries: Handle cases where the MCP server or agent fails gracefully.

## Response snapshot

Created comprehensive architecture plan with 12-step implementation roadmap for Phase 3 Part 3. Key decisions:
- **Self-hosted ChatKit** (ADR-007): Use ChatKit Python SDK on our FastAPI backend to integrate with existing JWT auth, agent, and database — not OpenAI-hosted mode.
- **ChatKit streaming** (ADR-008): Use built-in SSE streaming via ChatKitServer, avoiding ~200 lines of custom streaming code.
- **localStorage persistence** (ADR-009): Persist conversation_id in localStorage for session continuity, cleared on logout.

Architecture: ChatKit React component → POST /api/chatkit → TodoChatKitServer (ChatKitServer subclass) → run_agent() → MCP tools → Neon DB. Component diagram, data flow, error flow, and auth bridge documented. Submission readiness checklist covers all Phase 2 and Phase 3 requirements.

## Outcome

- ✅ Impact: Architecture plan and 3 ADRs created for Phase 3 Part 3
- 🧪 Tests: None (plan phase — test strategy defined in roadmap step 10)
- 📁 Files: plan.md + 3 ADRs created
- 🔁 Next prompts: /sp.tasks to create implementation task breakdown
- 🧠 Reflection: ChatKit Python SDK provides a clean abstraction (ChatKitServer + Store) that maps well to our existing backend. Self-hosted mode is the correct choice since we have a fully functional agent and auth system. Key risk is ChatKit Store adapter complexity.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (plan phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate ChatKit Python SDK Store interface compatibility with our SQLModel models before implementation
