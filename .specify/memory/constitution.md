<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Modified principles:
  - Principle IV "Full-Stack Integration with Modern Technologies" → expanded to include AI/MCP stack components
  - Principle V "Security-First with Proper Authentication" → expanded to cover MCP tool authentication and user isolation in AI context
  - Principle VI "Cloud-Native and Scalable Architecture" → expanded to include stateless chat architecture
Added sections:
  - Principle VII "MCP-First Tool Architecture"
  - Principle VIII "Stateless Conversational AI with Database-Backed Persistence"
  - Principle IX "AI Agent Behavior and Natural Language Interface"
  - Technology Stack Compliance updated with Phase III components
  - New "AI and MCP Architecture Standards" section under Additional Constraints
  - New "Conversation and State Management" section under Additional Constraints
Removed sections: None
Templates requiring updates:
  - `.specify/templates/plan-template.md` ⚠ pending (may need MCP component planning section)
  - `.specify/templates/spec-template.md` ⚠ pending (may need MCP tool specification section)
  - `.specify/templates/tasks-template.md` ⚠ pending (may need AI/MCP task categories)
Follow-up TODOs: None
-->

# Hackathon Todo Constitution

## Core Principles

### I. Spec-Driven Development (SDD) - NON-NEGOTIABLE
All development MUST follow the Spec-Driven Development methodology using Claude Code and Spec-Kit Plus. No code shall be written without a corresponding specification in the specs/ directory. The Specify → Plan → Tasks → Implement workflow MUST be strictly followed. This ensures that every implementation step maps back to an explicit requirement. MCP server tools, AI agent behavior, and chat endpoints MUST each have their own specification before implementation begins.

### II. AI-Native Development with Claude Code
The primary development approach MUST leverage Claude Code as the agentic environment. All code generation, refactoring, and implementation tasks MUST utilize Claude Code's capabilities. Manual coding is prohibited — all changes MUST be made through Claude Code with proper specification references. This applies equally to backend API code, MCP server tools, and frontend ChatKit integration.

### III. Reusable Intelligence and Agent Skills
Emphasis on creating reusable intelligence via Claude Code Subagents and Agent Skills. All common functionality MUST be encapsulated as reusable components that can be leveraged across different phases and features. MCP tools MUST be designed as self-contained, reusable operations that any AI agent can invoke. This promotes efficiency and consistency across the project lifecycle.

### IV. Full-Stack Integration with Modern Technologies
Implementation MUST follow the specified technology stack: Next.js for frontend, FastAPI for backend, SQLModel for ORM, Neon Serverless PostgreSQL for database, OpenAI ChatKit for conversational UI, OpenAI Agents SDK for AI logic, and Official MCP SDK for tool exposition. All components MUST work cohesively in a monorepo structure with proper API contracts and data flow between layers. The MCP server MUST integrate with the existing FastAPI backend, not duplicate its logic.

### V. Security-First with Proper Authentication
Authentication and authorization MUST be implemented using Better Auth with JWT tokens. Every API endpoint — including the chat endpoint — MUST require proper authentication and enforce user isolation. MCP tools MUST receive and validate user_id to ensure users can only access their own tasks. Security considerations MUST be prioritized in all architectural decisions, including AI agent interactions with the database.

### VI. Cloud-Native and Scalable Architecture
Design and implementation MUST consider cloud deployment from the beginning. Architecture MUST support horizontal scaling, stateless services, and cloud-native patterns. The chat endpoint MUST be stateless — all conversation state MUST be persisted to the database, enabling any server instance to handle any request. Preparation for Kubernetes deployment (Minikube and cloud providers) MUST be considered in all design decisions.

### VII. MCP-First Tool Architecture
All task operations exposed to AI agents MUST be implemented as MCP tools using the Official MCP SDK. The MCP server MUST expose exactly five core tools: add_task, list_tasks, complete_task, delete_task, and update_task. Each tool MUST have clearly defined parameter schemas, structured return types, and descriptive metadata for AI agent introspection. MCP tools MUST be the single interface through which AI agents interact with the todo system — agents MUST NOT call REST endpoints directly.

### VIII. Stateless Conversational AI with Database-Backed Persistence
The chat system MUST follow a stateless request cycle: receive message → fetch conversation history from database → build agent context → run agent with MCP tools → store response → return to client. The server MUST hold NO in-memory conversation state between requests. Conversation and Message models MUST be persisted to Neon PostgreSQL alongside existing Task data. This architecture ensures resilience (server restarts do not lose state), horizontal scalability (any instance handles any request), and testability (each request is independent and reproducible).

### IX. AI Agent Behavior and Natural Language Interface
The AI agent powered by OpenAI Agents SDK MUST understand natural language commands for all five core task operations (create, list, complete, delete, update). The agent MUST always confirm actions with friendly responses and handle errors gracefully. The agent MUST use MCP tools as its sole mechanism for task manipulation — it MUST NOT generate raw SQL or bypass the MCP layer. When a user's intent is ambiguous, the agent MUST ask for clarification rather than guess.

## Additional Constraints and Requirements

### Technology Stack Compliance
- Frontend: Next.js 16+ with TypeScript, Tailwind CSS, and OpenAI ChatKit
- Backend: Python FastAPI with proper Pydantic models
- Database: Neon Serverless PostgreSQL with SQLModel ORM
- Authentication: Better Auth with JWT configuration
- AI Framework: OpenAI Agents SDK for agent logic and orchestration
- MCP Server: Official MCP SDK (Python) exposing task operations as tools
- Deployment: Docker containers, Helm charts for Kubernetes
- Chat UI: OpenAI ChatKit with domain allowlist configuration for production

### AI and MCP Architecture Standards
- The MCP server MUST expose tools with clear parameter schemas and descriptions
- Each MCP tool MUST accept user_id as a required parameter for user isolation
- MCP tool responses MUST return structured JSON with task_id, status, and relevant data
- The OpenAI Agents SDK agent MUST be configured with all five MCP tools
- The chat endpoint (POST /api/{user_id}/chat) MUST accept conversation_id (optional) and message (required)
- The chat response MUST include conversation_id, response text, and tool_calls array
- Agent behavior MUST map natural language intents to appropriate MCP tool calls

### Conversation and State Management
- Conversation model: user_id, id, created_at, updated_at
- Message model: user_id, id, conversation_id, role (user/assistant), content, created_at
- New conversations MUST be created when no conversation_id is provided
- Existing conversations MUST be resumed when a valid conversation_id is provided
- Full message history MUST be loaded from the database and passed to the agent for context
- Both user messages and assistant responses MUST be stored in the database immediately

### Quality Standards
- All code MUST be properly tested with adequate test coverage
- Clean code principles and proper project structure MUST be maintained
- Proper error handling and input validation MUST be implemented
- Documentation MUST be maintained for all public interfaces
- Proper logging and observability MUST be integrated
- MCP tools MUST include error handling for task-not-found and invalid input scenarios
- Agent responses MUST be tested for correct tool selection given natural language inputs

## Development Workflow and Quality Gates

### Spec Compliance
- All development MUST reference specific spec files (specs/features/, specs/api/, specs/database/, specs/ui/)
- No features may be implemented without corresponding specification
- Specifications MUST be updated when requirements change
- All code files MUST contain comments linking to relevant Task and Spec sections
- MCP tool implementations MUST reference the MCP tools specification

### Code Review and Testing
- All changes MUST pass automated testing before merging
- Peer review is required for all substantial changes
- Performance and security considerations MUST be validated
- API contracts MUST remain backward compatible unless explicitly planned as breaking change
- Database migrations MUST be properly tested and reversible
- MCP tool responses MUST be validated against the defined schema
- Chat endpoint MUST be tested for conversation creation, resumption, and multi-turn interactions

### Phase-Based Delivery
- Each hackathon phase MUST be completed before advancing to the next
- Phase III requires: conversational interface via ChatKit, OpenAI Agents SDK integration, MCP server with five core tools, stateless chat endpoint with database-backed conversation persistence
- All Basic Level functionality (Add, Delete, Update, View, Mark Complete) MUST be accessible through both the web UI (Phase II) and the chatbot (Phase III)
- Proper separation of concerns: ChatKit UI → Chat Endpoint → Agents SDK → MCP Tools → Database

## Governance

This constitution represents the binding agreement for all development activities in the Hackathon Todo project. All contributors MUST adhere to these principles and guidelines. Any deviation from these principles requires explicit amendment to this constitution with proper justification and approval. All pull requests and code reviews MUST verify compliance with these principles. Complexity MUST be justified with clear benefits and documented reasoning.

The hierarchy of authority is: Constitution > Specify > Plan > Tasks. If a conflict arises between spec files, the Constitution takes precedence.

**Version**: 1.1.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-07
