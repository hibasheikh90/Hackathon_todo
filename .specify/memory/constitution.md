# Evolution of Todo - Project Constitution

**Project:** Hackathon II - Evolution of Todo
**Version:** 1.0
**Ratified:** 2025-12-29
**Last Amended:** 2025-12-29

## Purpose

This constitution defines the immutable principles, constraints, and standards for building the Evolution of Todo project - a five-phase journey from a simple console application to a cloud-native, AI-powered distributed system.

---

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

**WHY:** AI agents become more powerful when guided by clear specifications rather than vibe-coding.

**RULES:**
- ✅ **MUST** write specifications before any code
- ✅ **MUST** use Claude Code + Spec-Kit Plus workflow: Specify → Plan → Tasks → Implement
- ❌ **NEVER** write code manually - refine specs until Claude Code generates correct output
- ✅ **MUST** maintain spec history in `/specs` folder
- ✅ **MUST** document all AI interactions and iterations
- ✅ **MUST** link every code change back to a task and spec section

### II. AI-Native Architecture

**WHY:** The future of software is AI-native; engineers are system architects, not syntax writers.

**RULES:**
- ✅ **MUST** use OpenAI Agents SDK for AI agent logic (Phase III+)
- ✅ **MUST** use Official MCP SDK for Model Context Protocol servers (Phase III+)
- ✅ **MUST** implement stateless servers with database-persisted state
- ✅ **MUST** design for natural language interfaces
- ❌ **NEVER** hardcode AI behavior - use tool-based architectures

### III. Cloud-Native First

**WHY:** Modern applications must be scalable, resilient, and cloud-ready from day one.

**RULES:**
- ✅ **MUST** containerize all services with Docker (Phase IV+)
- ✅ **MUST** use Kubernetes for orchestration (local Minikube → cloud DOKS/GKE/AKS)
- ✅ **MUST** implement event-driven architecture with Kafka (Phase V)
- ✅ **MUST** use Dapr for distributed application runtime (Phase V)
- ✅ **MUST** design for horizontal scalability
- ❌ **NEVER** couple services tightly - use message queues and service meshes

### IV. Progressive Enhancement

**WHY:** Build iteratively with each phase adding complexity while maintaining previous functionality.

**RULES:**
- ✅ **MUST** complete phases in order: I → II → III → IV → V
- ✅ **MUST** ensure each phase is fully functional before moving to next
- ✅ **MUST** maintain backward compatibility when adding features
- ✅ **MUST** deliver working demos at each checkpoint
- ❌ **NEVER** skip phases or merge phase requirements

### V. Security by Design

**WHY:** User data must be protected and isolated from day one.

**RULES:**
- ✅ **MUST** implement JWT-based authentication (Phase II+)
- ✅ **MUST** filter all queries by authenticated user ID
- ✅ **MUST** use environment variables for secrets
- ✅ **MUST** validate all user inputs
- ❌ **NEVER** commit secrets to Git
- ❌ **NEVER** trust client-provided user IDs without JWT verification
- ❌ **NEVER** return other users' data

### VI. Stateless Services (Phase III+)

**WHY:** Stateless servers enable horizontal scaling, resilience, and cloud-native deployment.

**RULES:**
- ✅ **MUST** persist all state to database (conversation history, tasks)
- ✅ **MUST** design servers to handle any request without session memory
- ✅ **MUST** support horizontal scaling via load balancers
- ❌ **NO** in-memory session caching
- ❌ **NO** sticky sessions

### VII. Event-Driven Architecture (Phase V)

**WHY:** Services should communicate via events, not direct API calls, for loose coupling and scalability.

**RULES:**
- ✅ **MUST** publish task operations to Kafka topics
- ✅ **MUST** use separate consumer services (reminders, recurring tasks, audit)
- ✅ **MUST** design for eventual consistency
- ❌ **NO** synchronous inter-service calls for business logic

---

## Technology Stack (Fixed Constraints)

### Phase I: Console Application
- **Language:** Python 3.13+
- **Package Manager:** UV
- **Development:** Claude Code + Spec-Kit Plus
- **Storage:** In-memory

### Phase II: Full-Stack Web Application
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth with JWT |
| Deployment | Vercel (Frontend) |

### Phase III: AI Chatbot
| Component | Technology |
|-----------|------------|
| Chat UI | OpenAI ChatKit |
| AI Framework | OpenAI Agents SDK |
| MCP Server | Official MCP SDK (Python) |
| Architecture | Stateless chat endpoint + MCP tools |

### Phase IV: Local Kubernetes
| Component | Technology |
|-----------|------------|
| Containerization | Docker Desktop |
| Docker AI | Gordon (Docker AI Agent) |
| Orchestration | Minikube |
| Package Manager | Helm Charts |
| AI DevOps | kubectl-ai, kagent |

### Phase V: Advanced Cloud Deployment
| Component | Technology |
|-----------|------------|
| Cloud Platform | DigitalOcean DOKS / Google GKE / Azure AKS / Oracle OKE |
| Event Streaming | Kafka (Strimzi self-hosted or Redpanda Cloud) |
| Distributed Runtime | Dapr (Pub/Sub, State, Bindings, Secrets, Service Invocation) |
| CI/CD | GitHub Actions |

**CONSTRAINTS:**
- ❌ **CANNOT** substitute core technologies (FastAPI, Next.js, SQLModel, etc.)
- ✅ **MAY** add supporting libraries within the approved stack
- ❌ **CANNOT** use different AI SDKs (must use OpenAI Agents SDK + Official MCP SDK)

---

## Code Quality Standards

### 1. Clean Code Principles

**RULES:**
- ✅ **MUST** follow language-specific style guides (PEP 8 for Python, ESLint for Next.js)
- ✅ **MUST** use descriptive variable and function names
- ✅ **MUST** keep functions small and single-purpose
- ✅ **MUST** write self-documenting code; comments explain "why", not "what"
- ❌ **NEVER** leave commented-out code
- ❌ **NEVER** use magic numbers - define constants

### 2. Project Structure

**Backend (FastAPI):**
```
backend/
├── main.py              # FastAPI app entry point
├── models.py            # SQLModel database models
├── routes/              # API route handlers
│   ├── tasks.py
│   └── chat.py
├── db.py                # Database connection
├── auth.py              # JWT verification middleware
├── mcp_server/          # MCP tools (Phase III+)
│   └── tools.py
└── requirements.txt
```

**Frontend (Next.js):**
```
frontend/
├── app/                 # App Router pages
│   ├── page.tsx         # Home/task list
│   └── chat/page.tsx    # Chatbot (Phase III)
├── components/          # Reusable UI components
├── lib/
│   └── api.ts           # Backend API client
└── package.json
```

**Specs (Spec-Kit Plus):**
```
specs/
├── overview.md
├── architecture.md
├── features/
│   ├── task-crud.md
│   ├── authentication.md
│   └── chatbot.md
├── api/
│   ├── rest-endpoints.md
│   └── mcp-tools.md
├── database/
│   └── schema.md
└── ui/
    ├── components.md
    └── pages.md
```

### 3. Error Handling

**PATTERNS:**
- ✅ Use `try/except` with specific exceptions (Python)
- ✅ Use error boundaries (Next.js)
- ✅ Log errors with context (task ID, user ID)
- ✅ Return user-friendly error messages
- ❌ NO bare `except:` clauses
- ❌ NO silent failures

**HTTP Status Codes:**
- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid JWT
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server-side failures

### 4. Testing Requirements

**MINIMUM STANDARDS:**
- ✅ **MUST** test all API endpoints (unit tests)
- ✅ **MUST** test MCP tools independently (Phase III+)
- ✅ **MUST** verify user isolation in tests
- ✅ **SHOULD** include integration tests for critical flows
- ✅ **SHOULD** test error paths, not just happy paths

**DELIVERABLE:**
- ✅ Working demos at each phase
- ✅ 90-second demo video showing all features

---

## Security Standards

### 1. Authentication & Authorization

**MECHANISM:** Better Auth (Phase II+) with JWT tokens

**FLOW:**
1. User logs in → Better Auth issues JWT
2. Frontend includes JWT in `Authorization: Bearer <token>` header
3. Backend verifies JWT signature with shared secret
4. Backend extracts `user_id` and filters data by ownership

**RULES:**
- ✅ **MUST** validate JWT on every API request
- ✅ **MUST** filter all queries by authenticated user ID
- ✅ **MUST** use same `BETTER_AUTH_SECRET` in frontend + backend
- ❌ **NEVER** trust client-provided user IDs without JWT verification
- ❌ **NEVER** return other users' data

### 2. User Data Isolation

**PRINCIPLE:** Users only see their own tasks.

**ENFORCEMENT:**
- ✅ All database queries include `WHERE user_id = <authenticated_user>`
- ✅ MCP tools accept `user_id` parameter and validate against JWT claims
- ✅ REST endpoints include `/api/{user_id}/tasks` pattern
- ❌ NO global task lists without user filtering

### 3. Secrets Management

**RULES:**
- ✅ **MUST** use `.env` files for local development
- ✅ **MUST** use Kubernetes Secrets or Dapr Secrets API in production
- ✅ **MUST** document all required secrets in README
- ❌ **NEVER** commit secrets to Git
- ❌ **NEVER** hardcode API keys, passwords, or tokens

**REQUIRED SECRETS:**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT signing key (shared frontend + backend)
- `OPENAI_API_KEY` - For OpenAI Agents SDK
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` - For ChatKit (Phase III)

### 4. Input Validation

**RULES:**
- ✅ **MUST** validate all user inputs (title length, field types)
- ✅ **MUST** sanitize data before database insertion
- ✅ **MUST** return appropriate HTTP status codes (400, 401, 404, 500)
- ❌ **NEVER** trust client data without validation
- ❌ **NEVER** expose internal errors to clients (use generic messages)

---

## Performance Standards

### 1. API Response Times

**TARGETS:**
- ✅ REST endpoints: < 200ms p95 latency
- ✅ Chat endpoint: < 2s p95 (including AI inference)
- ✅ Database queries: < 100ms p95

**OPTIMIZATION:**
- ✅ Use database indexes (user_id, completed, created_at)
- ✅ Limit query results (pagination for task lists)
- ✅ Use async/await for I/O operations (Python asyncio, Next.js)

### 2. Scalability

**REQUIREMENTS:**
- ✅ Stateless servers (can add replicas horizontally)
- ✅ Database connection pooling
- ✅ Event-driven decoupling (Phase V)
- ❌ NO in-memory state that prevents scaling

### 3. Resource Limits

**CONSTRAINTS:**
- ✅ Use Neon serverless DB (free tier: 0.5 GB storage, 100 hours compute/month)
- ✅ Optimize Docker images (use multi-stage builds)
- ✅ Set Kubernetes resource requests/limits
- ❌ NO unbounded loops or recursive calls

---

## Feature Requirements

### Basic Level (Core Essentials) - All Phases

**MANDATORY FEATURES:**
1. ✅ Add Task - Create with title & description
2. ✅ Delete Task - Remove by ID
3. ✅ Update Task - Modify title/description
4. ✅ View Task List - Display all tasks
5. ✅ Mark as Complete - Toggle completion status

**USER STORIES:**
- As a user, I can create a new task with a title and optional description
- As a user, I can view all my tasks with their completion status
- As a user, I can update the title or description of an existing task
- As a user, I can delete a task I no longer need
- As a user, I can mark a task as complete or incomplete

### Intermediate Level (Phase V)

**OPTIONAL FEATURES:**
1. ✅ Priorities & Tags - High/medium/low, categories (work/home)
2. ✅ Search & Filter - By keyword, status, priority, date
3. ✅ Sort Tasks - By due date, priority, alphabetically

### Advanced Level (Phase V)

**OPTIONAL FEATURES:**
1. ✅ Recurring Tasks - Auto-reschedule (daily, weekly, monthly)
2. ✅ Due Dates & Reminders - Date/time pickers, browser notifications

---

## Natural Language Interface (Phase III+)

### Chatbot Behavior Specification

**AI AGENT RULES:**
| User Intent | Agent Action | MCP Tool |
|-------------|--------------|----------|
| "Add/create/remember X" | Create task | `add_task` |
| "Show/list my tasks" | Retrieve tasks | `list_tasks` |
| "Mark X as done/complete" | Complete task | `complete_task` |
| "Delete/remove X" | Delete task | `delete_task` |
| "Change/update X to Y" | Update task | `update_task` |

**RESPONSE STYLE:**
- ✅ Conversational and friendly
- ✅ Confirm actions ("✓ Added task: Buy groceries")
- ✅ Handle ambiguity ("Which task did you mean? 1) Call mom, 2) Email mom")
- ✅ Graceful error handling ("I couldn't find that task. Try 'show all tasks' to see your list.")
- ❌ NO robotic responses
- ❌ NO exposing technical errors to users

**EXAMPLE INTERACTIONS:**
```
User: "Add a task to buy groceries"
Bot: "✓ Added: Buy groceries"

User: "What's on my list?"
Bot: "You have 3 tasks:
1. Buy groceries (pending)
2. Call mom (pending)
3. Finish report (completed)"

User: "Mark groceries as done"
Bot: "✓ Marked complete: Buy groceries"
```

---

## Event-Driven Patterns (Phase V)

### Kafka Event Schema

**Task Event:**
```json
{
  "event_type": "created | updated | completed | deleted",
  "task_id": 123,
  "task_data": { "title": "...", "description": "...", "completed": false },
  "user_id": "user_uuid",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Reminder Event:**
```json
{
  "task_id": 123,
  "title": "Task title",
  "due_at": "2025-01-15T14:00:00Z",
  "remind_at": "2025-01-15T13:00:00Z",
  "user_id": "user_uuid"
}
```

### Consumer Services

**RESPONSIBILITIES:**
| Service | Consumes | Produces | Purpose |
|---------|----------|----------|---------|
| **Recurring Task Service** | `task-events` (completed) | `task-events` (created) | Spawn next occurrence |
| **Notification Service** | `reminders` | Push notifications | Send due date alerts |
| **Audit Service** | `task-events` (all) | Audit logs | Compliance trail |
| **WebSocket Service** | `task-updates` | WebSocket messages | Real-time sync |

---

## Deployment Standards

### 1. Version Control

**RULES:**
- ✅ **MUST** use Git with meaningful commit messages
- ✅ **MUST** maintain public GitHub repository
- ✅ **MUST** include all specs in `/specs` folder
- ✅ **MUST** include CLAUDE.md and README.md at root
- ❌ **NEVER** commit `.env` files or secrets

**COMMIT MESSAGE FORMAT:**
```
<type>: <subject>

<body - explain why, reference spec>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

### 2. Documentation Requirements

**MANDATORY FILES:**
- ✅ `README.md` - Setup instructions, tech stack, how to run
- ✅ `CLAUDE.md` - Claude Code instructions (reference AGENTS.md)
- ✅ `/specs/**/*.md` - All feature specifications
- ✅ `.specify/memory/constitution.md` - This file
- ✅ Demo video link (< 90 seconds)

**README SECTIONS:**
1. Project Overview
2. Technology Stack (per phase)
3. Setup Instructions (local + cloud)
4. Environment Variables
5. Running the Application
6. Project Structure
7. Deployment Guide

### 3. Containerization (Phase IV+)

**DOCKER STANDARDS:**
- ✅ Use official base images (python:3.13-slim, node:20-alpine)
- ✅ Multi-stage builds to reduce image size
- ✅ `.dockerignore` to exclude unnecessary files
- ✅ Non-root user for security
- ✅ Health checks in Dockerfile

### 4. Kubernetes Deployment (Phase IV+)

**HELM CHART STRUCTURE:**
```
helm-charts/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   └── ingress.yaml
```

**RULES:**
- ✅ Use Helm for package management
- ✅ Use kubectl-ai and kagent for AI-assisted operations
- ✅ Define resource requests/limits for all pods
- ✅ Use ConfigMaps for non-secret configuration
- ✅ Use Secrets for sensitive data
- ❌ NO hardcoded values in YAML (use Helm values)

### 5. CI/CD Pipeline (Phase V)

**GITHUB ACTIONS WORKFLOW:**
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  test:
    - Run tests
  build:
    - Build Docker images
    - Push to registry
  deploy:
    - Deploy to Kubernetes with Helm
```

**GATES:**
- ✅ All tests pass
- ✅ Docker images build successfully
- ✅ Helm charts validate
- ❌ NO manual deployments to production

---

## Governance

### Constitution Hierarchy

This constitution supersedes all other practices and documentation. When conflicts arise:

1. **Constitution** (this file) - Immutable principles and constraints
2. **Spec files** (`/specs/**/*.md`) - Feature requirements and architecture
3. **Code comments** - Implementation-level documentation

### Amendment Process

**RULES:**
- ✅ **MUST** document reason for amendment
- ✅ **MUST** get explicit approval before changing principles
- ✅ **MUST** create migration plan if affecting existing code
- ✅ **MUST** update version number and amendment date

### Compliance

**ENFORCEMENT:**
- ✅ All PRs/reviews must verify compliance with this constitution
- ✅ Complexity and deviations must be justified
- ✅ Use CLAUDE.md for runtime development guidance
- ❌ NO shortcuts that violate core principles

### Success Criteria

**PHASE GATES:**
- Each phase must meet its success criteria before proceeding
- Working demo required at each checkpoint
- All mandatory features must be implemented
- Specs must be complete and approved

### Submission Requirements

**EVERY PHASE:**
- ✅ Public GitHub repository
- ✅ `/specs` folder with all specifications
- ✅ CLAUDE.md and README.md
- ✅ Demo video (< 90 seconds)
- ✅ WhatsApp number (for presentation invitation)

**PHASE-SPECIFIC:**
- **Phase II:** Vercel URL + Backend API URL
- **Phase III-V:** Chatbot URL
- **Phase IV:** Minikube setup instructions
- **Phase V:** Cloud deployment URL + CI/CD workflow

---

## Non-Negotiables (Hard Constraints)

### MUST DO
1. ✅ Use Spec-Driven Development for every phase
2. ✅ Complete phases in order (I → II → III → IV → V)
3. ✅ Use the specified technology stack (no substitutions)
4. ✅ Implement user authentication and data isolation (Phase II+)
5. ✅ Use stateless server architecture (Phase III+)
6. ✅ Deploy to cloud (Phase V)
7. ✅ Submit working demos at each checkpoint

### NEVER DO
1. ❌ Write code manually (must use Claude Code + Spec-Kit Plus)
2. ❌ Skip phases or merge requirements
3. ❌ Substitute core technologies
4. ❌ Commit secrets to Git
5. ❌ Deploy stateful servers (Phase III+)
6. ❌ Allow cross-user data access
7. ❌ Submit without working demo

---

**This constitution is the immutable source of truth for all AI agents and developers working on this project. When in doubt, refer to this document.**

**Version:** 1.0 | **Ratified:** 2025-12-29 | **Last Amended:** 2025-12-29
