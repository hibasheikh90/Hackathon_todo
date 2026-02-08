---
id: 001
title: OpenAI Agents SDK and Auth Integration Specification
stage: spec
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 2-openai-agents-chat-interface
branch: 2-openai-agents-chat-interface
user: hayas
command: /sp.specify
labels: ["spec", "openai-agents-sdk", "auth-bridge", "chat-endpoint", "phase3-part2"]
links:
  spec: specs/2-openai-agents-chat-interface/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/2-openai-agents-chat-interface/spec.md
tests:
  - N/A (specification phase)
---

## Prompt

/sp.specify "Phase 3 Part 2: OpenAI Agents SDK and Auth Integration"

Objective:
Implement the core AI Agent logic to orchestrate user requests and securely interface with the Phase 2 backend using the MCP tools developed in Part 1.

Scope:
- Integrate the OpenAI Agents SDK to manage the conversational reasoning loop.
- Implement an Authentication Bridge: Extract the JWT token from the frontend request and inject it into the MCP tool calls.
- Define the Agent's "Cognitive Stance": Use the P+Q+P pattern (Persona + Questions + Principles) to ensure the agent is a precise, task-oriented productivity assistant.

Acceptance Criteria:
- The Agent can successfully identify the current user via the JWT token.
- The Agent refuses to perform actions if a valid JWT is missing or expired.
- The Agent can handle multi-step natural language intents (e.g., "Find my tasks for today and mark the first one as complete").
- Memory Management: The Agent maintains short-term conversational context within a single session.

Constraints:
- Must use existing MCP tools from Part 1 as-is via stdio transport.

## Response snapshot

Created comprehensive feature specification at `specs/2-openai-agents-chat-interface/spec.md` with:
- 6 user stories covering core chat flow, conversation context, auth bridge, P+Q+P cognitive stance, multi-step intents, and conversation persistence
- 15 functional requirements (FR-001 through FR-015)
- 8 success criteria (SC-001 through SC-008)
- 6 edge cases (MCP failure, API key missing, context overflow, timeout, concurrency, empty message)
- New entities: Conversation, Message models
- Integration points: existing JWT auth, MCP server (Part 1), OpenAI Agents SDK, AsyncSessionLocal
- Expected file structure with new files and unchanged existing files

## Outcome

- ✅ Impact: Specification defines the complete scope for Phase 3 Part 2 chat interface with auth integration
- 🧪 Tests: N/A (specification phase — tests defined in acceptance scenarios)
- 📁 Files: 1 file created (spec.md)
- 🔁 Next prompts: `/sp.plan` to create the architecture plan, then `/sp.tasks` to break into testable tasks
- 🧠 Reflection: Spec builds directly on Part 1 MCP server. Auth bridge pattern (JWT → user_id injection) is the key security design. Agent behavior defined via P+Q+P pattern. Stateless architecture with DB-backed conversation persistence.

## Evaluation notes (flywheel)

- Failure modes observed: User input truncated at "Must us" — recovered via clarifying question
- Graders run and results (PASS/FAIL): Manual review — PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to plan phase
