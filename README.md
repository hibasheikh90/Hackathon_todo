# Hackathon Todo - Phase I: Console Application

**Version:** 1.0.0
**Phase:** I of V
**Status:** Complete

## Overview

This is Phase I of the **Evolution of Todo** project - a five-phase journey from a simple console application to a cloud-native, AI-powered distributed system. Phase I implements a command-line todo application with in-memory storage, establishing the foundation for future phases.

**Key Achievement:** Spec-Driven Development using Claude Code and Spec-Kit Plus - zero lines of code written manually!

## Features

Phase I implements all 5 Basic Level features:

- ✅ **Add Task** - Create new tasks with title and optional description
- ✅ **View All Tasks** - Display tasks in a formatted table with completion status
- ✅ **Update Task** - Modify task title and/or description
- ✅ **Delete Task** - Remove tasks with confirmation prompt
- ✅ **Mark Complete/Incomplete** - Toggle task completion status

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.13+ |
| **Package Manager** | UV |
| **Architecture** | Layered (CLI → Business Logic → Data) |
| **Storage** | In-memory (Python dictionary) |
| **Development** | Claude Code + Spec-Kit Plus |

## Prerequisites

Before running this application, ensure you have:

- **Python 3.13+** installed ([Download](https://www.python.org/downloads/))
- **UV** package manager installed

### Installing UV

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hackathon-todo.git
cd hackathon-todo
```

### 2. Install Dependencies

```bash
uv sync
```

*(Note: Phase I uses only Python standard library, so no external dependencies are required)*

## Usage

### Running the Application

**Option 1: Using UV (Recommended)**
```bash
uv run python -m src.main
```

**Option 2: Using Python directly**
```bash
python -m src.main
```

### Main Menu

```
==================================================
  TODO APP - PHASE I
==================================================

------------------------------
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Exit
------------------------------
Enter your choice (1-6):
```

### Example Session

```
1. Add Task
   Enter task title: Buy groceries
   Enter description (optional): Milk, eggs, bread
   [SUCCESS] Task added successfully! (ID: 1, Title: "Buy groceries")

2. View All Tasks
   ----------------------------------------------------------------------
   ID    Status   Title                                    Description
   ----------------------------------------------------------------------
   1     [ ]      Buy groceries                            Milk, eggs, ...
   ----------------------------------------------------------------------

5. Mark Task Complete/Incomplete
   Enter task ID: 1
   [SUCCESS] Task marked as complete: "Buy groceries"

2. View All Tasks
   ----------------------------------------------------------------------
   ID    Status   Title                                    Description
   ----------------------------------------------------------------------
   1     [X]      Buy groceries                            Milk, eggs, ...
   ----------------------------------------------------------------------

6. Exit
   Thank you for using Todo App! Goodbye.
```

## Project Structure

```
hackathon_todo/
├── .specify/
│   └── memory/
│       └── constitution.md      # Project principles and standards
├── specs/
│   └── phase1-console/
│       ├── spec.md              # Phase I requirements
│       ├── plan.md              # Architecture and design
│       └── tasks.md             # Implementation tasks
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── menu.py              # CLI menu and user interaction
│   │   └── display.py           # Output formatting
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py            # Task dataclass
│   │   └── task_manager.py     # Business logic (CRUD operations)
│   └── utils/
│       ├── __init__.py
│       ├── validators.py        # Input validation
│       └── formatters.py        # String formatting utilities
├── .gitignore
├── pyproject.toml
├── CLAUDE.md                    # Claude Code development guide
├── hackathon.md                 # Full hackathon requirements
└── README.md                    # This file
```

## Development

### Spec-Driven Development Workflow

This project was built using Spec-Driven Development with Claude Code:

1. **Specify (WHAT)** → `specs/phase1-console/spec.md` - Requirements defined
2. **Plan (HOW)** → `specs/phase1-console/plan.md` - Architecture designed
3. **Tasks (BREAKDOWN)** → `specs/phase1-console/tasks.md` - 12 implementation tasks
4. **Implement (CODE)** → Claude Code executed all tasks

**Zero lines of code written manually!**

### Architecture

```
┌─────────────────────────────┐
│   Presentation Layer        │
│   (CLI Menu + Display)      │
└─────────────┬───────────────┘
              │
┌─────────────▼───────────────┐
│   Business Logic Layer      │
│   (TaskManager)             │
└─────────────┬───────────────┘
              │
┌─────────────▼───────────────┐
│   Data Layer                │
│   (In-Memory Dict)          │
└─────────────────────────────┘
```

### Code Quality

- ✅ Type hints on all functions
- ✅ Docstrings (Google style)
- ✅ PEP 8 compliant
- ✅ Separation of concerns
- ✅ Error handling with user-friendly messages

## Testing

### Manual Test Scenarios

All 12 test cases from the specification passed:

- ✅ Add task with title only
- ✅ Add task with title + description
- ✅ Add task with empty title → Error message
- ✅ View tasks (empty list) → Friendly message
- ✅ View tasks with multiple items → Table display
- ✅ Update task title → Success
- ✅ Update task description → Success
- ✅ Update non-existent task → Error
- ✅ Delete task with confirmation → Removed
- ✅ Mark task complete → Status changes to [X]
- ✅ Toggle completed task → Status reverts to [ ]
- ✅ Exit application → Graceful shutdown

## Limitations (By Design)

Phase I has intentional limitations that will be addressed in future phases:

- **No Persistence** - Data is lost when the application exits (Phase II adds database)
- **Single User** - No authentication or multi-user support (Phase II adds auth)
- **No Network** - Console-only, no web interface (Phase II adds web app)
- **No AI** - No natural language interface (Phase III adds chatbot)

## Next Phases

### Phase II: Full-Stack Web Application (Coming Soon)
- Next.js 16+ frontend
- FastAPI backend
- Neon Serverless PostgreSQL
- Better Auth with JWT
- RESTful API

### Phase III: AI-Powered Chatbot
- OpenAI ChatKit UI
- OpenAI Agents SDK
- Official MCP SDK
- Natural language todo management

### Phase IV: Local Kubernetes Deployment
- Docker containerization
- Minikube deployment
- Helm charts
- kubectl-ai and kagent for AIOps

### Phase V: Cloud-Native Production
- DigitalOcean/GKE/AKS deployment
- Kafka event streaming
- Dapr distributed runtime
- CI/CD with GitHub Actions

## Contributing

This is a hackathon project following strict Spec-Driven Development principles. All code is generated via Claude Code based on detailed specifications.

## License

MIT License

## Author

**Hackathon II Participant**
Built with Claude Code and Spec-Kit Plus

---

## Quick Start Summary

```bash
# Install UV (if not already installed)
# See Prerequisites section above

# Clone repository
git clone https://github.com/yourusername/hackathon-todo.git
cd hackathon-todo

# Run application
uv run python -m src.main
```

**Enjoy your spec-driven todo app!** 🚀
