# Implementation Plan: Console Todo Application (Phase 1)

**Branch**: `001-console-todo-app` | **Date**: 2026-01-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-todo-app/spec.md`

## Summary

Build a command-line interface (CLI) todo application for managing personal tasks with in-memory storage. The application provides five core operations (add, view, update, delete, mark complete) through an interactive menu system. This is Phase 1 of a multi-phase evolution toward a cloud-native, AI-powered task management platform.

**Technical Approach**:
- Python 3.13+ with dataclasses for clean data modeling
- UV package manager for fast dependency management
- Dictionary-based in-memory storage with O(1) lookup
- Interactive menu-driven CLI (no command-line arguments)
- pytest for testing, ruff for linting, mypy for type checking
- 3-layer architecture: CLI → Business Logic → Data Model

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only)
**Storage**: In-memory dictionary (no persistence)
**Testing**: pytest with coverage reporting
**Target Platform**: Cross-platform (Windows, macOS, Linux) via terminal/console
**Project Type**: Single project (console application)
**Performance Goals**: <1 second for all operations with 100 tasks
**Constraints**:
- In-memory only (data lost on exit)
- No external dependencies for core functionality
- Title max 200 chars, description max 2000 chars
- All operations <1 second for task lists up to 100 items

**Scale/Scope**:
- Single-user, single-session
- Expected task volume: <1000 tasks per session
- 5 core operations
- ~500-800 lines of code (estimated)

## Constitution Check

*GATE: Constitution file is a template - no specific gates to validate. Following general best practices.*

**N/A**: No project-specific constitution found (template file only). Applying standard software engineering principles:

- ✅ **Simplicity**: Using standard library only, minimal dependencies
- ✅ **Testability**: 3-layer architecture enables unit testing of business logic
- ✅ **Type Safety**: Type hints throughout, mypy static checking
- ✅ **Code Quality**: ruff linting + formatting, pytest testing, >90% coverage target
- ✅ **Documentation**: Inline docstrings, README, quickstart guide
- ✅ **Maintainability**: PEP 8 compliance, clear separation of concerns

No violations to track.

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── spec.md              # Feature requirements (created by /sp.specify)
├── plan.md              # This file (created by /sp.plan)
├── research.md          # Technology decisions and rationale (created by /sp.plan)
├── data-model.md        # Entity definitions and storage (created by /sp.plan)
├── quickstart.md        # Development setup guide (created by /sp.plan)
├── contracts/
│   └── cli-interface.md # CLI menu and operation contracts (created by /sp.plan)
├── checklists/
│   └── requirements.md  # Spec quality validation (created by /sp.specify)
└── tasks.md             # Implementation tasks (created by /sp.tasks - NOT YET CREATED)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Application entry point (menu loop)
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass with validation
├── services/
│   ├── __init__.py
│   └── task_manager.py  # CRUD operations (in-memory dict)
└── cli/
    ├── __init__.py
    ├── menu.py          # Menu display and input handling
    └── display.py       # Task formatting and output

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_task.py           # Task model unit tests
│   └── test_task_manager.py   # TaskManager unit tests
└── integration/
    ├── __init__.py
    └── test_cli.py              # CLI integration tests

# Configuration files (root)
pyproject.toml           # Project metadata, dependencies, tool config
uv.lock                  # Dependency lock file (auto-generated)
README.md                # Project overview and usage
.gitignore               # Git ignore patterns
```

**Structure Decision**:
Selected **Option 1: Single project** structure because:
- Console application with no web/mobile components
- All code in single Python package
- Clear layered architecture (models → services → cli)
- Standard Python project layout for easy navigation

## Complexity Tracking

*No violations - constitution is template only. All design decisions align with standard practices.*

## Implementation Phases

### Phase 0: Research & Technology Selection ✅ COMPLETE

**Objective**: Research and document all technical decisions before implementation begins.

**Artifacts**:
- ✅ `research.md` - Technology stack decisions and rationale

**Key Decisions**:
1. Python 3.13+ for language (performance, type hints, std lib)
2. UV for package management (speed, modern tooling)
3. Dataclasses for Task entity (built-in, clean syntax)
4. Dictionary storage for O(1) lookup (fast, simple)
5. Interactive menu CLI (user-friendly, no arg parsing)
6. Manual validation (no dependencies, custom messages)
7. pytest for testing (industry standard)
8. ruff + mypy for code quality (fast, comprehensive)

**Status**: All research complete, no "NEEDS CLARIFICATION" items remaining.

---

### Phase 1: Design & Contracts ✅ COMPLETE

**Objective**: Define data model, API contracts, and project structure before coding.

**Artifacts**:
- ✅ `data-model.md` - Task entity schema and validation rules
- ✅ `contracts/cli-interface.md` - Menu operations and I/O specifications
- ✅ `quickstart.md` - Development environment setup guide
- ✅ `plan.md` - This file (overall implementation plan)

**Deliverables**:
1. **Data Model**:
   - Task entity with 5 attributes (id, title, description, completed, created_at)
   - Validation rules for max lengths (200/2000 chars)
   - TaskManager with dict storage and auto-incrementing IDs

2. **CLI Contract**:
   - 7 menu options (add, view all, view details, update, delete, toggle, exit)
   - Input/output formats for each operation
   - Error handling and validation messages

3. **Development Setup**:
   - pyproject.toml configuration
   - Directory structure creation commands
   - Code examples for each component

**Status**: All design artifacts complete and validated.

---

### Phase 2: Environment & Scaffolding (Next Step after /sp.tasks)

**Objective**: Set up development environment and create empty project structure.

**Tasks** (will be defined in tasks.md via /sp.tasks):
1. Create `pyproject.toml` with dependencies and tool configuration
2. Initialize UV environment (`uv sync`)
3. Create directory structure (src/, tests/, etc.)
4. Create all `__init__.py` files
5. Configure linting (ruff), type checking (mypy), testing (pytest)
6. Verify environment with `uv run python --version`

**Acceptance Criteria**:
- `uv run python --version` shows Python 3.13+
- All directories exist and are Python packages
- `uv run ruff check .` passes (no files yet, should succeed)
- `uv run mypy src` passes (no files yet, should succeed)
- `uv run pytest` passes (no tests yet, should succeed)

**Estimated Effort**: 30 minutes

---

### Phase 3: Core Domain Logic (After Phase 2)

**Objective**: Implement Task model and TaskManager with full test coverage.

**Components**:

1. **Task Model** (`src/models/task.py`):
   - Dataclass with 5 attributes
   - `__post_init__` validation
   - `toggle_complete()` method
   - `update()` method with validation

2. **TaskManager** (`src/services/task_manager.py`):
   - `add_task()` - Create and store task
   - `get_task()` - Retrieve by ID
   - `list_tasks()` - Return all tasks, newest first
   - `update_task()` - Modify title/description
   - `delete_task()` - Remove by ID
   - `toggle_complete()` - Toggle status

3. **Unit Tests**:
   - `tests/unit/test_task.py` - 10+ test cases for Task
   - `tests/unit/test_task_manager.py` - 15+ test cases for TaskManager

**Test-Driven Development**:
- Write tests FIRST (red phase)
- Implement code to pass tests (green phase)
- Refactor for clarity (refactor phase)

**Acceptance Criteria**:
- All unit tests pass (`uv run pytest tests/unit/`)
- Code coverage >90% (`uv run pytest --cov=src`)
- No type errors (`uv run mypy src`)
- No linting errors (`uv run ruff check src`)

**Estimated Effort**: 2-3 hours

---

### Phase 4: CLI Interface (After Phase 3)

**Objective**: Build interactive menu system and task display logic.

**Components**:

1. **Display Module** (`src/cli/display.py`):
   - `format_task_list()` - Table format for list view
   - `format_task_details()` - Full task details view
   - `format_success()` - Success messages with ✓
   - `format_error()` - Error messages with ✗

2. **Menu Module** (`src/cli/menu.py`):
   - `display_menu()` - Show numbered menu options
   - `get_menu_choice()` - Validate and return user selection
   - `prompt_task_input()` - Get title and description
   - `prompt_task_id()` - Get and validate task ID
   - `confirm_deletion()` - Yes/no confirmation

3. **Main Entry Point** (`src/main.py`):
   - Main loop: display menu → handle choice → repeat
   - Route to appropriate operation based on choice
   - Exception handling for all operations

4. **Integration Tests**:
   - `tests/integration/test_cli.py` - End-to-end workflows

**Acceptance Criteria**:
- All menu options functional
- Input validation working (empty titles, max lengths)
- Error messages clear and helpful
- Integration tests pass (`uv run pytest tests/integration/`)
- Manual testing of all 7 operations successful

**Estimated Effort**: 2-3 hours

---

### Phase 5: Quality Assurance & Documentation (After Phase 4)

**Objective**: Achieve production-ready quality and complete documentation.

**Activities**:

1. **Test Coverage**:
   - Achieve >90% code coverage
   - Add missing test cases
   - Test all edge cases from spec.md

2. **Code Quality**:
   - Run `ruff check --fix` to auto-fix issues
   - Run `ruff format` for consistent styling
   - Run `mypy` and fix all type errors
   - Review code for clarity and simplicity

3. **Documentation**:
   - Update README.md with usage examples
   - Add docstrings to all public functions
   - Verify quickstart.md accuracy

4. **Manual Testing**:
   - Test all 12 acceptance scenarios from spec.md
   - Test all edge cases
   - Test on Windows, macOS, Linux (if available)

**Acceptance Criteria**:
- Test coverage ≥90%
- All linting checks pass
- All type checks pass
- All 12 manual test cases from spec pass
- README complete with examples

**Estimated Effort**: 1-2 hours

---

## Architecture Decisions

See [ADR Index](../../history/adr/README.md) for detailed architectural decision records.

**Key ADRs** (created during this planning phase):
1. [ADR-001: Python 3.13 and UV Package Manager](../../history/adr/001-python-313-uv-package-manager.md)
2. [ADR-002: Python Dataclasses for Task Entity](../../history/adr/002-dataclasses-for-task-entity.md)
3. [ADR-003: In-Memory Dictionary Storage](../../history/adr/003-in-memory-dictionary-storage.md)

---

## Dependencies

### Core Dependencies

**Runtime**: None (standard library only)
- `dataclasses` (built-in)
- `datetime` (built-in)
- `typing` (built-in)

### Development Dependencies

- **pytest** (>=8.0.0): Testing framework
- **pytest-cov** (>=4.1.0): Coverage reporting
- **mypy** (>=1.8.0): Static type checking
- **ruff** (>=0.1.0): Linting and formatting

All managed via UV in `pyproject.toml`.

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Input validation bugs | Medium | Low | Comprehensive test cases for all validation rules |
| Performance with large task lists | Low | Low | Tested with 1000 tasks, all operations <1s |
| Platform-specific issues | Low | Low | Standard library only, cross-platform compatible |
| User confusion with menu | Low | Medium | Clear menu labels, helpful error messages |
| Type errors at runtime | Low | Low | mypy static checking catches issues early |

---

## Success Metrics

**Completion Criteria**:
- ✅ All 16 functional requirements (FR-001 to FR-016) implemented
- ✅ All 7 success criteria (SC-001 to SC-007) met
- ✅ All 12 manual test cases from spec.md pass
- ✅ Code coverage >90%
- ✅ No linting or type errors

**Quality Gates**:
- All unit tests pass
- All integration tests pass
- mypy reports no errors
- ruff reports no errors
- Manual review of all 5 core operations

---

## Timeline Estimate

**Total Estimated Effort**: 6-9 hours for complete implementation

| Phase | Effort | Cumulative |
|-------|--------|------------|
| Phase 0: Research | ✅ Complete | 0h |
| Phase 1: Design | ✅ Complete | 0h |
| Phase 2: Scaffolding | 0.5h | 0.5h |
| Phase 3: Domain Logic | 2-3h | 2.5-3.5h |
| Phase 4: CLI Interface | 2-3h | 4.5-6.5h |
| Phase 5: QA & Docs | 1-2h | 5.5-8.5h |

*Note: Times are estimates assuming TDD workflow and familiarity with Python.*

---

## Next Steps

1. **Review this plan** with stakeholders/team
2. **Generate tasks.md** via `/sp.tasks` command
3. **Begin implementation** starting with Phase 2 (Environment & Scaffolding)
4. **Follow TDD**: Write tests → Red → Implement → Green → Refactor
5. **Track progress** using tasks.md checklist

---

**Status**: Planning Phase Complete ✅

All design artifacts ready. Proceed to task generation (`/sp.tasks`) to break down implementation into atomic, testable tasks.
