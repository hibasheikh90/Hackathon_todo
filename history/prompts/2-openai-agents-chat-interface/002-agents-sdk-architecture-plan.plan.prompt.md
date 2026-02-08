---
id: 002
title: OpenAI Agents SDK Architecture Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 2-openai-agents-chat-interface
branch: 2-openai-agents-chat-interface
user: hayas
command: /sp.plan
labels: ["plan", "openai-agents-sdk", "auth-bridge", "architecture", "phase3-part2"]
links:
  spec: specs/2-openai-agents-chat-interface/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/2-openai-agents-chat-interface/plan.md
tests:
  - N/A (planning phase)
---

## Prompt

/sp.plan "Phase 3 Part 2: OpenAI Agent Orchestration and Secure Auth Bridge"

Instructions:
1. Review the Phase 3 Part 1 MCP tools and the Phase 2 FastAPI backend security.
2. Generate Architectural Decision Records (ADRs) for:
   - Agent Persona (P+Q+P): Define the specific Persona, Questions, and Principles the Agent uses.
   - Context Injection Strategy: How the Agent will receive the JWT from the frontend and inject it into MCP tool headers.
   - Error Recovery Policy: How the Agent should handle failed tool calls or expired auth tokens.
3. Create a multi-step roadmap including:
   - Initializing the OpenAI Agents SDK orchestration loop.
   - Implementing the logic to map natural language intents to MCP tool sequences.
   - Configuring the System Prompt based on the project Constitution.
Focus on Data Isolation and Security.

## Response snapshot

Created comprehensive architecture plan at `specs/2-openai-agents-chat-interface/plan.md` with:
- Constitution check (9 principles, all PASS)
- Component diagram showing JWT → ChatService → Agent → MCP → DB pipeline
- Auth bridge flow diagram showing user_id injection from JWT to MCP tools
- 8-step implementation roadmap (dependency setup → error handling)
- Data flow for single chat request (10-step orchestration)
- Error flow mapping (7 error types → HTTP status codes)
- 2 new database models (Conversation, Message)
- 4 risks identified with mitigations
- 5 key architectural decisions (3 new ADRs suggested + 2 inherited from Part 1)

Key architectural decisions:
1. Auth bridge: user_id extracted from JWT, injected into agent instructions, LLM passes to MCP tools
2. P+Q+P cognitive stance: Persona (productivity assistant) + Questions (clarify ambiguity) + Principles (confirm, handle errors, stay on-topic)
3. Error recovery: tool failures → friendly message, expired JWT → 401 before agent, MCP failure → 503
4. MCPServerStdio: spawn MCP server as subprocess per request (Part 1 reused as-is)

## Outcome

- ✅ Impact: Architecture plan fully defines the agent orchestration, auth bridge, and conversation persistence layers
- 🧪 Tests: N/A (planning phase — test strategy defined in roadmap Step 7)
- 📁 Files: 1 file created (plan.md)
- 🔁 Next prompts: ADR creation for decisions 004/005/006, then `/sp.tasks` to break into testable tasks
- 🧠 Reflection: Key insight from OpenAI Agents SDK research: MCP tool context injection does NOT auto-forward to subprocess. Must use agent instructions to tell LLM which user_id to use. This is consistent with ADR-002 (user_id passthrough pattern). Risk: LLM could hallucinate wrong user_id — mitigated by MCP schema validation requiring the parameter.

## Evaluation notes (flywheel)

- Failure modes observed: User input truncated again at last bullet — pattern suggests clipboard/terminal limit
- Graders run and results (PASS/FAIL): Manual review — PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create ADRs 004-006, then proceed to tasks
