---
id: 002
title: MCP Server Architecture Plan
stage: plan
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 1-mcp-server-todo-tools
branch: main
user: hayas
command: /sp.plan
labels: ["phase3", "mcp", "plan", "architecture", "adr"]
links:
  spec: specs/1-mcp-server-todo-tools/spec.md
  ticket: null
  adr: history/adr/001-mcp-transport-stdio.md, history/adr/002-auth-bridge-user-id-passthrough.md, history/adr/003-tool-schema-design.md
  pr: null
files:
  - specs/1-mcp-server-todo-tools/plan.md
  - specs/1-mcp-server-todo-tools/research.md
  - specs/1-mcp-server-todo-tools/data-model.md
  - specs/1-mcp-server-todo-tools/quickstart.md
  - specs/1-mcp-server-todo-tools/contracts/mcp-tools-schema.json
  - history/adr/001-mcp-transport-stdio.md
  - history/adr/002-auth-bridge-user-id-passthrough.md
  - history/adr/003-tool-schema-design.md
tests:
  - null
---

## Prompt

/sp.plan "Phase 3 Part 1: MCP Server and Tooling Architecture"

Instructions:
1. Review the existing Phase 2 FastAPI codebase and the newly created Phase 3 Part 1 Specification.
2. Generate Architectural Decision Records (ADRs) for:
   - MCP Transport: Select between Stdio and HTTP/SSE.
   - Authentication Bridge: How the MCP server will extract JWT from the client and pass it to the FastAPI backend.
   - Tool Schema: Define the input/output structure for the 5 core Todo tools.
3. Create a multi-step roadmap including:
   - Setup of the @modelcontextprotocol/sdk.
   - Mapping of FastAPI endpoints to MCP Tools.
   - Integration testing with the MCP Inspector.

Focus on:
- Intelligence Reuse: Ensure the tools are descriptive enough so the Agent understands "why" and "when" to call them.
- Security: Zero-trust approach—every tool call must validate the user identity.

## Response snapshot

Generated complete implementation plan with 8 artifacts:

**Plan artifacts:**
- `plan.md` — 10-step roadmap from dependency setup through automated tests, component diagram, data flow, endpoint-to-tool mapping, risk analysis
- `research.md` — 6 research decisions: MCP SDK API patterns, stdio vs HTTP transport, DB session management, auth bridge, OpenAI Agents SDK integration, TaskService compatibility
- `data-model.md` — No new entities; documents existing Task/User models + all 5 MCP tool input/output JSON schemas
- `quickstart.md` — Setup, run, and verify instructions for MCP Inspector and OpenAI Agents SDK
- `contracts/mcp-tools-schema.json` — Formal JSON Schema contract for all 5 tools with inputSchema and outputSchema

**ADRs (3):**
- ADR-001: Stdio transport selected over HTTP/SSE — subprocess isolation, MCPServerStdio compatibility, no network attack surface
- ADR-002: User ID passthrough — JWT validated at FastAPI chat endpoint, user_id passed as explicit tool parameter, SQL-level isolation
- ADR-003: Descriptive tool schemas — intent-based descriptions ("Use this when..."), type hints auto-generate JSON Schema, consistent JSON string returns

**Key architectural decision:** MCP server reuses TaskService in-process (direct DB access) rather than calling REST endpoints. Auth is enforced at the FastAPI boundary; MCP trusts user_id because it runs as a subprocess.

## Outcome

- Impact: Complete implementation blueprint ready for /sp.tasks to break into atomic work units
- Tests: N/A (plan phase)
- Files: 8 artifacts created across specs/ and history/adr/
- Next prompts: /sp.tasks to generate implementation tasks from the plan
- Reflection: The plan correctly identifies the key risk (TaskOwnershipError inheriting HTTPException) and provides mitigation. The 10-step roadmap is sequenced to enable incremental testing — each step produces a testable increment.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify list_tasks needs to use async_task_crud directly (not TaskService) for the completed filter parameter
