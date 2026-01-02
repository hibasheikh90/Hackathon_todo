---
description: "Implementation tasks for Console Todo Application Phase 1"
---

# Tasks: Console Todo Application (Phase 1)

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md

**Tests**: Tests are included per spec requirement for code quality (>90% coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create pyproject.toml with project metadata, Python 3.13+ requirement, and dev dependencies (pytest, pytest-cov, mypy, ruff)
- [x] T002 Initialize UV environment with `uv sync` to create virtual environment and install dependencies
- [x] T003 [P] Create directory structure: src/, src/models/, src/services/, src/cli/, tests/, tests/unit/, tests/integration/
- [x] T004 [P] Create all __init__.py files: src/__init__.py, src/models/__init__.py, src/services/__init__.py, src/cli/__init__.py, tests/__init__.py, tests/unit/__init__.py, tests/integration/__init__.py
- [x] T005 [P] Create .gitignore file with Python-specific ignore patterns (.venv/, __pycache__/, *.pyc, .pytest_cache/, .coverage, .mypy_cache/)
- [x] T006 [P] Create README.md with project overview, installation instructions, and usage examples
- [x] T007 Verify environment setup: run `uv run python --version` to confirm Python 3.13+

**Checkpoint**: Project structure ready - all directories exist, dependencies installed, environment verified

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain model and business logic that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 [P] Create Task dataclass in src/models/task.py with attributes (id: int, title: str, description: str, completed: bool, created_at: datetime)
- [x] T009 [P] Implement Task.__post_init__ validation in src/models/task.py (title not empty, title ≤200 chars, description ≤2000 chars)
- [x] T010 [P] Implement Task.toggle_complete() method in src/models/task.py
- [x] T011 [P] Implement Task.update() method in src/models/task.py with validation for title and description
- [x] T012 Create TaskManager class in src/services/task_manager.py with internal state (_tasks: dict[int, Task], _next_id: int)
- [x] T013 Implement TaskManager.add_task(title, description) in src/services/task_manager.py with ID assignment and validation
- [x] T014 [P] Implement TaskManager.get_task(task_id) in src/services/task_manager.py with None return for missing IDs
- [x] T015 [P] Implement TaskManager.list_tasks() in src/services/task_manager.py returning tasks sorted newest-first by created_at
- [x] T016 [P] Implement TaskManager.update_task(task_id, title, description) in src/services/task_manager.py
- [x] T017 [P] Implement TaskManager.delete_task(task_id) in src/services/task_manager.py with bool return for success/failure
- [x] T018 [P] Implement TaskManager.toggle_complete(task_id) in src/services/task_manager.py

**Checkpoint**: Foundation ready - Task model and TaskManager fully implemented with all CRUD operations

---

## Phase 3: User Story 1 - Quick Task Capture (Priority: P1) 🎯 MVP

**Goal**: Allow users to add new tasks with title and optional description so they can capture todo items without friction

**Independent Test**: Launch app, select "Add Task", enter title and description, verify task appears in list with correct ID and status

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T019 [P] [US1] Create tests/unit/test_task.py with test cases for Task creation, validation (empty title, max lengths), toggle_complete(), and update()
- [x] T020 [P] [US1] Create tests/unit/test_task_manager.py with test cases for add_task (success, validation errors, ID assignment, newest-first ordering)

### Implementation for User Story 1

- [x] T021 [US1] Create display module in src/cli/display.py with format_success(message) and format_error(message) functions using ✓ and ✗ symbols
- [x] T022 [US1] Implement prompt_task_input() in src/cli/menu.py to collect title and description with validation loop for empty title and max lengths
- [x] T023 [US1] Add handle_add_task(manager) function in src/main.py to call prompt_task_input(), manager.add_task(), and display success with ID
- [x] T024 [US1] Create main menu loop in src/main.py with menu display, input handling, and routing to handle_add_task for option 1
- [x] T025 [US1] Add error handling in handle_add_task() for ValueError exceptions from validation failures
- [x] T026 [US1] Run unit tests for User Story 1: `uv run pytest tests/unit/test_task.py tests/unit/test_task_manager.py -v`

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks and see success messages

---

## Phase 4: User Story 2 - Task List Overview (Priority: P1) 🎯 MVP

**Goal**: Allow users to view all tasks in a clear, organized list so they can see what they need to do at a glance

**Independent Test**: Add several tasks (both complete and incomplete), select "View Tasks", verify all tasks displayed with correct status indicators in newest-first order

### Tests for User Story 2

- [x] T027 [P] [US2] Add test cases to tests/unit/test_task_manager.py for list_tasks() with empty list, multiple tasks, and ordering verification
- [x] T028 [P] [US2] Create tests/integration/test_cli.py with integration test for add task → view list workflow

### Implementation for User Story 2

- [x] T029 [P] [US2] Implement format_task_list(tasks) in src/cli/display.py to display table with ID, Status ([x] or [ ]), and Title columns (newest first)
- [x] T030 [P] [US2] Implement format_task_details(task) in src/cli/display.py to show full task information including description and created_at timestamp
- [x] T031 [US2] Add handle_view_all_tasks(manager) function in src/main.py to call manager.list_tasks() and display.format_task_list()
- [x] T032 [US2] Add handle_view_task_details(manager) function in src/main.py to prompt for ID, call manager.get_task(), and display full details
- [x] T033 [US2] Update main menu loop in src/main.py to route option 2 to handle_view_all_tasks and option 3 to handle_view_task_details
- [x] T034 [US2] Add empty state handling in handle_view_all_tasks() to display "No tasks found" message when list is empty
- [x] T035 [US2] Add error handling in handle_view_task_details() for invalid ID input and task not found
- [x] T036 [US2] Run integration tests for User Story 2: `uv run pytest tests/integration/test_cli.py -v -k "test_view"`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add and view tasks

---

## Phase 5: User Story 3 - Task Completion Tracking (Priority: P2)

**Goal**: Allow users to mark tasks as complete or incomplete so they can track progress and distinguish between finished and pending work

**Independent Test**: Create tasks, mark them complete, view list to verify status changes to [x], toggle back to verify status changes to [ ]

### Tests for User Story 3

- [x] T037 [P] [US3] Add test cases to tests/unit/test_task_manager.py for toggle_complete() with valid ID, invalid ID, and state verification
- [x] T038 [P] [US3] Add integration test to tests/integration/test_cli.py for add task → toggle complete → view list workflow

### Implementation for User Story 3

- [x] T039 [US3] Implement prompt_task_id(prompt_message) in src/cli/menu.py to get and validate task ID input (integer check, ValueError handling)
- [x] T040 [US3] Add handle_toggle_complete(manager) function in src/main.py to prompt for ID, call manager.toggle_complete(), and display success with status
- [x] T041 [US3] Update main menu loop in src/main.py to route option 6 to handle_toggle_complete
- [x] T042 [US3] Add error handling in handle_toggle_complete() for invalid ID and task not found scenarios
- [x] T043 [US3] Run tests for User Story 3: `uv run pytest tests/ -v -k "test_toggle"`

**Checkpoint**: User Stories 1, 2, and 3 all work independently - users can add, view, and mark tasks complete

---

## Phase 6: User Story 4 - Task Updates (Priority: P3)

**Goal**: Allow users to edit existing tasks so they can correct mistakes or update information as work evolves

**Independent Test**: Create task, select "Update Task", modify title and/or description, verify changes reflected in task list and details view

### Tests for User Story 4

- [x] T044 [P] [US4] Add test cases to tests/unit/test_task.py for Task.update() method with various combinations (title only, description only, both, validation)
- [x] T045 [P] [US4] Add test cases to tests/unit/test_task_manager.py for update_task() with valid/invalid IDs and validation scenarios
- [x] T046 [P] [US4] Add integration test to tests/integration/test_cli.py for add → update → view details workflow

### Implementation for User Story 4

- [x] T047 [US4] Implement prompt_task_update(current_title, current_description) in src/cli/menu.py to get new values with "press Enter to keep" option
- [x] T048 [US4] Add handle_update_task(manager) function in src/main.py to prompt for ID, display current task, prompt for updates, call manager.update_task()
- [x] T049 [US4] Update main menu loop in src/main.py to route option 4 to handle_update_task
- [x] T050 [US4] Add validation in handle_update_task() to preserve current values when user presses Enter without input
- [x] T051 [US4] Add error handling in handle_update_task() for invalid ID, task not found, and validation errors
- [x] T052 [US4] Run tests for User Story 4: `uv run pytest tests/ -v -k "test_update"`

**Checkpoint**: User Stories 1-4 all work independently - full CRUD operations except delete

---

## Phase 7: User Story 5 - Task Removal (Priority: P3)

**Goal**: Allow users to delete tasks that are no longer relevant so they can keep task list clean and focused

**Independent Test**: Create tasks, select "Delete Task", confirm deletion, verify task removed from list

### Tests for User Story 5

- [x] T053 [P] [US5] Add test cases to tests/unit/test_task_manager.py for delete_task() with valid ID, invalid ID, and verification task is removed
- [x] T054 [P] [US5] Add integration test to tests/integration/test_cli.py for add → delete → view list workflow (including cancellation)

### Implementation for User Story 5

- [x] T055 [US5] Implement confirm_deletion(task_title) in src/cli/menu.py to prompt "Delete task '{title}'? (y/n)" with validation loop
- [x] T056 [US5] Add handle_delete_task(manager) function in src/main.py to prompt for ID, get task, confirm, call manager.delete_task()
- [x] T057 [US5] Update main menu loop in src/main.py to route option 5 to handle_delete_task
- [x] T058 [US5] Add cancellation handling in handle_delete_task() to display "Deletion cancelled" when user enters 'n'
- [x] T059 [US5] Add error handling in handle_delete_task() for invalid ID and task not found
- [x] T060 [US5] Run tests for User Story 5: `uv run pytest tests/ -v -k "test_delete"`

**Checkpoint**: All user stories (1-5) complete - full CRUD operations functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure production quality

- [x] T061 [P] Add display_menu() function in src/cli/menu.py with all 7 menu options (1-6, 0 for exit) and formatted header
- [x] T062 [P] Add get_menu_choice() function in src/cli/menu.py to validate menu input and handle invalid selections
- [x] T063 Update main loop in src/main.py to use display_menu() and get_menu_choice() with continuous loop until exit (option 0)
- [x] T064 Add handle_exit() function in src/main.py to display goodbye message "Thanks for using Todo App! All data will be cleared on exit."
- [x] T065 Update main menu loop in src/main.py to route option 0 to handle_exit and break loop
- [x] T066 [P] Add comprehensive docstrings to all public functions in src/models/task.py, src/services/task_manager.py, src/cli/display.py, src/cli/menu.py
- [x] T067 [P] Run ruff linting and auto-fix: `uv run ruff check --fix src tests`
- [x] T068 [P] Run ruff formatting: `uv run ruff format src tests`
- [x] T069 [P] Run mypy type checking: `uv run mypy src` and fix all type errors
- [x] T070 Run full test suite with coverage: `uv run pytest --cov=src --cov-report=term-missing` and verify >90% coverage
- [x] T071 Add missing test cases to reach 90% coverage target (focus on edge cases from spec.md)
- [x] T072 Update README.md with complete usage examples, all 7 menu operations, and example session output
- [x] T073 [P] Manual testing: Execute all 12 acceptance scenarios from spec.md and verify pass
- [x] T074 [P] Manual testing: Execute all edge cases from spec.md (special characters, max lengths, invalid IDs, etc.)
- [x] T075 Verify quickstart.md accuracy by following setup instructions in fresh environment

**Checkpoint**: Production-ready application - all quality gates passed, documentation complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3 → P3)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1/US2)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1-3)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1-4)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services (already in Foundational phase for this project)
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 Setup**: T003, T004, T005, T006 can run in parallel
- **Phase 2 Foundational**: T008-T011 (Task model) can run in parallel; T014-T018 (TaskManager methods) can run in parallel after T012-T013
- **Phase 3 US1 Tests**: T019, T020 can run in parallel
- **Phase 4 US2 Tests**: T027, T028 can run in parallel; T029, T030 can run in parallel
- **Phase 5 US3 Tests**: T037, T038 can run in parallel
- **Phase 6 US4 Tests**: T044, T045, T046 can run in parallel
- **Phase 7 US5 Tests**: T053, T054 can run in parallel
- **Phase 8 Polish**: T061, T062, T066, T067, T068, T069, T073, T074 can run in parallel
- **Once Foundational completes**: All user stories (Phases 3-7) can start in parallel if team capacity allows

---

## Parallel Example: Foundational Phase (Phase 2)

```bash
# Launch all Task model tasks together:
T008: "Create Task dataclass in src/models/task.py"
T009: "Implement Task.__post_init__ validation in src/models/task.py"
T010: "Implement Task.toggle_complete() method in src/models/task.py"
T011: "Implement Task.update() method in src/models/task.py"

# After TaskManager class created (T012), launch all TaskManager methods together:
T014: "Implement TaskManager.get_task(task_id) in src/services/task_manager.py"
T015: "Implement TaskManager.list_tasks() in src/services/task_manager.py"
T016: "Implement TaskManager.update_task(task_id, title, description) in src/services/task_manager.py"
T017: "Implement TaskManager.delete_task(task_id) in src/services/task_manager.py"
T018: "Implement TaskManager.toggle_complete(task_id) in src/services/task_manager.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T018) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T019-T026)
4. Complete Phase 4: User Story 2 (T027-T036)
5. **STOP and VALIDATE**: Test User Stories 1 and 2 independently
6. Deploy/demo MVP with core add and view functionality

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 (P1) → Test independently → Deploy/Demo (MVP - can add and view tasks!)
3. Add User Story 3 (P2) → Test independently → Deploy/Demo (can now track completion)
4. Add User Story 4 + 5 (P3) → Test independently → Deploy/Demo (full CRUD operations)
5. Polish (Phase 8) → Final quality gates → Production release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Quick Task Capture)
   - Developer B: User Story 2 (Task List Overview)
   - Developer C: User Story 3 (Task Completion Tracking)
3. Stories complete and integrate independently
4. Developers D & E can work on User Stories 4 & 5 in parallel with A, B, C

---

## Task Summary

**Total Tasks**: 75
- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 11 tasks (BLOCKING)
- **Phase 3 (US1 - P1)**: 8 tasks
- **Phase 4 (US2 - P1)**: 10 tasks
- **Phase 5 (US3 - P2)**: 7 tasks
- **Phase 6 (US4 - P3)**: 9 tasks
- **Phase 7 (US5 - P3)**: 8 tasks
- **Phase 8 (Polish)**: 15 tasks

**Parallel Opportunities**: 38 tasks marked [P] can run in parallel (51% of tasks)

**Independent Test Criteria**:
- **US1**: Can add tasks and see success confirmation
- **US2**: Can view task list with correct status indicators
- **US3**: Can toggle task completion status
- **US4**: Can update task title and description
- **US5**: Can delete tasks with confirmation

**Suggested MVP Scope**: Phases 1, 2, 3, 4 (US1 + US2) = 36 tasks (48% of total)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run `uv run pytest` frequently to verify tests pass
- Run `uv run ruff check src` and `uv run mypy src` to maintain code quality
- Follow contracts/cli-interface.md for exact input/output formats
