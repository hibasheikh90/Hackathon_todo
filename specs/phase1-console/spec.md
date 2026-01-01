# Phase I: Todo In-Memory Python Console App - Specification

**Version:** 1.0
**Phase:** I of V
**Status:** Draft
**Created:** 2026-01-01
**Last Updated:** 2026-01-01

---

## 1. Purpose & Overview

### 1.1 Objective
Build a command-line todo application that stores tasks in memory using Python 3.13+. This application serves as the foundation for the Evolution of Todo project, establishing core CRUD operations that will be enhanced in subsequent phases.

### 1.2 Scope
**In Scope:**
- Basic task CRUD operations (Create, Read, Update, Delete)
- Task completion status toggling
- In-memory data storage
- Command-line interface (CLI)
- Interactive menu system

**Out of Scope:**
- Persistent storage (comes in Phase II)
- Multi-user support (comes in Phase II)
- Authentication (comes in Phase II)
- AI/chatbot interface (comes in Phase III)
- Cloud deployment (comes in Phase IV-V)

### 1.3 Success Criteria
- ✅ All 5 Basic Level features fully functional
- ✅ Clean, well-structured Python code following PEP 8
- ✅ No runtime errors or crashes during normal operation
- ✅ Graceful error handling for invalid inputs
- ✅ Professional user experience with clear prompts and feedback
- ✅ Deliverable includes: `/src` folder, README.md, CLAUDE.md, constitution.md

---

## 2. User Stories

### US-1: Create Task
**As a** user
**I want to** add a new task with a title and optional description
**So that** I can track things I need to do

**Acceptance Criteria:**
- User can enter a task title (required, 1-200 characters)
- User can optionally enter a description (max 1000 characters)
- System assigns a unique ID to each task
- System confirms task creation with a success message
- Task is immediately visible in the task list

### US-2: View All Tasks
**As a** user
**I want to** see a list of all my tasks
**So that** I can review what needs to be done

**Acceptance Criteria:**
- Display shows all tasks with ID, title, and completion status
- Completed tasks are visually distinguished from pending tasks
- Empty list shows a helpful message ("No tasks yet. Add one to get started!")
- Tasks are displayed in creation order (newest first or oldest first - to be decided)

### US-3: Update Task
**As a** user
**I want to** modify an existing task's title or description
**So that** I can correct mistakes or update requirements

**Acceptance Criteria:**
- User can select a task by ID
- User can update title, description, or both
- User can choose to keep existing values unchanged
- System confirms successful update
- Invalid task IDs show a clear error message

### US-4: Delete Task
**As a** user
**I want to** remove a task from my list
**So that** I can clean up completed or cancelled tasks

**Acceptance Criteria:**
- User can select a task by ID to delete
- System asks for confirmation before deletion
- System confirms successful deletion
- Invalid task IDs show a clear error message
- Deleted tasks are immediately removed from the list

### US-5: Mark Task Complete/Incomplete
**As a** user
**I want to** toggle a task's completion status
**So that** I can track my progress

**Acceptance Criteria:**
- User can select a task by ID to toggle status
- Pending tasks can be marked as complete
- Completed tasks can be marked as incomplete (toggle behavior)
- System confirms the new status
- Status change is immediately reflected in the task list
- Invalid task IDs show a clear error message

---

## 3. Functional Requirements

### 3.1 Core Features (Basic Level)

#### FR-1: Add Task
- **Input:** Title (required), Description (optional)
- **Validation:**
  - Title: 1-200 characters, non-empty after trimming whitespace
  - Description: 0-1000 characters
- **Processing:**
  - Generate unique integer ID (auto-incrementing)
  - Set completion status to `False` by default
  - Store task in memory (Python list or dictionary)
- **Output:** Success message with task ID and title

#### FR-2: List Tasks
- **Input:** None (or optional filter: all/pending/completed)
- **Processing:** Retrieve all tasks from memory
- **Output:** Formatted table or list showing:
  - Task ID
  - Title
  - Status indicator ([ ] for pending, [✓] for completed)
  - Optional: description preview (first 50 chars)

#### FR-3: Update Task
- **Input:** Task ID, new title (optional), new description (optional)
- **Validation:**
  - Task ID must exist
  - At least one field (title or description) must be updated
  - Same validation rules as Add Task
- **Processing:** Update task in memory
- **Output:** Success message with updated task details

#### FR-4: Delete Task
- **Input:** Task ID
- **Validation:** Task ID must exist
- **Processing:** Remove task from memory after confirmation
- **Output:** Success message with deleted task title

#### FR-5: Toggle Task Status
- **Input:** Task ID
- **Validation:** Task ID must exist
- **Processing:** Flip `completed` boolean value
- **Output:** Success message with new status

### 3.2 User Interface (CLI)

#### Main Menu
```
===== TODO APP - PHASE I =====

1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Exit

Enter your choice (1-6): _
```

#### Navigation
- Numbered menu for primary actions
- Clear input prompts with expected format
- "Return to main menu" option after each action
- Graceful exit with confirmation

---

## 4. Data Model

### 4.1 Task Entity

```python
Task = {
    "id": int,           # Unique identifier (auto-increment)
    "title": str,        # Task title (1-200 chars, required)
    "description": str,  # Task description (0-1000 chars, optional)
    "completed": bool,   # Completion status (default: False)
    "created_at": str,   # ISO 8601 timestamp (for future phases)
}
```

**Example:**
```python
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and coffee",
    "completed": False,
    "created_at": "2026-01-01T10:30:00"
}
```

### 4.2 Storage
- **Type:** In-memory (Python list or dictionary)
- **Persistence:** None (data lost when program exits - by design for Phase I)
- **Initial State:** Empty list/dict

---

## 5. Technical Specifications

### 5.1 Technology Stack
- **Language:** Python 3.13+
- **Package Manager:** UV
- **Dependencies:** Standard library only (no external packages)
- **Development:** Claude Code + Spec-Kit Plus

### 5.2 Project Structure
```
hackathon_todo/
├── .specify/
│   └── memory/
│       └── constitution.md
├── specs/
│   └── phase1-console/
│       ├── spec.md          # This file
│       ├── plan.md          # To be created
│       └── tasks.md         # To be created
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point, main menu loop
│   ├── task_manager.py      # TaskManager class (business logic)
│   ├── models.py            # Task data model
│   └── utils.py             # Input validation, formatting
├── tests/                   # Optional for Phase I
│   └── test_task_manager.py
├── README.md
├── CLAUDE.md
├── pyproject.toml           # UV project configuration
└── .gitignore
```

### 5.3 Code Quality Standards
- Follow PEP 8 style guide
- Use type hints (Python 3.13 features)
- Docstrings for all functions and classes
- No global variables (except constants)
- Error handling with try/except blocks
- Input validation before processing

### 5.4 Performance Requirements
- Task operations: < 10ms (in-memory, negligible for Phase I)
- Memory usage: < 50MB for 1000 tasks
- No performance bottlenecks (O(1) or O(n) operations only)

---

## 6. Error Handling

### 6.1 Input Validation Errors
| Error | User Input | Response |
|-------|------------|----------|
| Empty title | "" or whitespace only | "Error: Title cannot be empty." |
| Title too long | > 200 chars | "Error: Title must be 200 characters or less." |
| Description too long | > 1000 chars | "Error: Description must be 1000 characters or less." |
| Invalid task ID | Non-existent ID | "Error: Task ID {id} not found." |
| Invalid menu choice | Not 1-6 | "Error: Please enter a number between 1 and 6." |
| Non-numeric input | "abc" for ID | "Error: Please enter a valid number." |

### 6.2 Error Response Pattern
```
❌ Error: <clear, user-friendly message>
Press Enter to continue...
```

---

## 7. User Experience (UX) Requirements

### 7.1 Principles
- Clear, concise prompts
- Immediate feedback for all actions
- Visual distinction between success and error messages
- Consistent formatting throughout
- Minimize user typing (numbered choices where possible)

### 7.2 Success Messages
```
✅ Task added successfully! (ID: 1, Title: "Buy groceries")
✅ Task updated successfully!
✅ Task deleted: "Buy groceries"
✅ Task marked as complete: "Buy groceries"
✅ Task marked as incomplete: "Buy groceries"
```

### 7.3 Visual Indicators
- `[ ]` - Pending task
- `[✓]` - Completed task
- `✅` - Success message
- `❌` - Error message
- `=====` - Section dividers

---

## 8. Testing Requirements

### 8.1 Manual Testing Scenarios
For Phase I, manual testing is acceptable. Future phases will require automated tests.

**Test Cases:**
1. **TC-1:** Add task with title only → Task appears in list with default values
2. **TC-2:** Add task with title and description → Both values saved correctly
3. **TC-3:** Add task with empty title → Error message shown
4. **TC-4:** View tasks when list is empty → Helpful empty state message
5. **TC-5:** View tasks with 5+ tasks → All tasks displayed correctly
6. **TC-6:** Update task title → Changes reflected in list
7. **TC-7:** Update non-existent task ID → Error message shown
8. **TC-8:** Delete task with confirmation → Task removed from list
9. **TC-9:** Mark task as complete → Status changes from [ ] to [✓]
10. **TC-10:** Toggle completed task → Status changes from [✓] to [ ]
11. **TC-11:** All operations on non-existent ID → Appropriate error messages
12. **TC-12:** Exit application → Program terminates gracefully

### 8.2 Expected Behavior
- No crashes or unhandled exceptions
- All error messages are user-friendly
- All success messages are clear and confirmatory
- Data integrity maintained throughout session

---

## 9. Constraints & Assumptions

### 9.1 Constraints
- ✅ **MUST** use Python 3.13+
- ✅ **MUST** use UV for package management
- ✅ **MUST** store data in memory only (no files, no database)
- ✅ **MUST** implement all 5 Basic Level features
- ✅ **MUST** follow Spec-Driven Development workflow
- ❌ **CANNOT** write code manually - must use Claude Code

### 9.2 Assumptions
- User has Python 3.13+ installed
- User has UV installed
- User runs application from command line
- Single user, single session (no concurrency)
- Data loss on exit is acceptable (by design)
- User understands basic CLI navigation

### 9.3 Non-Functional Requirements
- **Usability:** Intuitive menu structure, clear prompts
- **Reliability:** No crashes during normal operation
- **Maintainability:** Clean code structure for future phases
- **Portability:** Works on Windows, macOS, Linux

---

## 10. Deliverables

### 10.1 Code Artifacts
- ✅ `/src` folder with Python source code
- ✅ Working `main.py` entry point
- ✅ Proper project structure (as defined in 5.2)

### 10.2 Documentation
- ✅ `README.md` - Setup instructions, how to run
- ✅ `CLAUDE.md` - Claude Code instructions
- ✅ `.specify/memory/constitution.md` - Project principles
- ✅ `specs/phase1-console/spec.md` - This file
- ✅ `specs/phase1-console/plan.md` - Architecture (next step)
- ✅ `specs/phase1-console/tasks.md` - Implementation tasks (after plan)

### 10.3 Demo Requirements
- ✅ Working console application
- ✅ Demonstrate all 5 Basic Level features
- ✅ Show error handling for invalid inputs
- ✅ Record 90-second demo video (for submission)

### 10.4 Submission Package
- ✅ Public GitHub repository
- ✅ All source code committed
- ✅ README with setup and run instructions
- ✅ Demo video link
- ✅ WhatsApp number for presentation invitation

---

## 11. Acceptance Criteria (Definition of Done)

Phase I is considered complete when:

- [ ] All 5 Basic Level features are implemented and functional
- [ ] User can add tasks with validation
- [ ] User can view all tasks in a clear format
- [ ] User can update task title and/or description
- [ ] User can delete tasks with confirmation
- [ ] User can toggle task completion status
- [ ] All error cases are handled gracefully
- [ ] Code follows PEP 8 and constitution standards
- [ ] README.md explains setup and usage
- [ ] CLAUDE.md provides development context
- [ ] Application runs without crashes
- [ ] Demo video (< 90 seconds) demonstrates all features
- [ ] All files committed to GitHub
- [ ] No secrets or sensitive data in repository

---

## 12. Next Steps

After this specification is approved:

1. **Create Plan** (`specs/phase1-console/plan.md`) - Architecture and design decisions
2. **Create Tasks** (`specs/phase1-console/tasks.md`) - Breakdown into actionable tasks
3. **Implement** - Execute tasks using Claude Code
4. **Test** - Verify all acceptance criteria
5. **Document** - Complete README and demo video
6. **Submit** - GitHub repo + demo video

---

## 13. References

- **Hackathon Requirements:** `hackathon.md`
- **Project Constitution:** `.specify/memory/constitution.md`
- **PEP 8 Style Guide:** https://peps.python.org/pep-0008/
- **Python 3.13 Documentation:** https://docs.python.org/3.13/

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-01 | Claude Code | Initial specification created |

---

**Status:** Ready for Plan phase
**Next Artifact:** `specs/phase1-console/plan.md`
