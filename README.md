# Console Todo Application

A command-line todo application with in-memory storage built with Python 3.13+.

## Features

- ✅ Add tasks with title and optional description
- ✅ View all tasks in a clear list
- ✅ View detailed task information
- ✅ Update task title and description
- ✅ Mark tasks as complete/incomplete
- ✅ Delete tasks with confirmation
- ✅ Interactive menu-driven interface

## Requirements

- Python 3.13 or higher
- UV package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hackathon_todo
```

2. Install dependencies using UV:
```bash
uv sync
```

## Usage

Run the application using UV:

```bash
uv run python -m src.main
```

Or use the installed command:

```bash
uv run todo
```

### Menu Options

When you run the application, you'll see an interactive menu:

```
=== Todo Application ===
1. Add Task
2. View All Tasks
3. View Task Details
4. Update Task
5. Delete Task
6. Toggle Complete
0. Exit

Select option:
```

Simply enter the number corresponding to the action you want to perform.

### Example Session

```bash
$ uv run python -m src.main

=== Todo Application ===
1. Add Task
2. View All Tasks
3. View Task Details
4. Update Task
5. Delete Task
6. Toggle Complete
0. Exit

Select option: 1

Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Milk, eggs, bread

✓ Task added successfully! (ID: 1)

=== Todo Application ===
[... menu repeats ...]

Select option: 2

=== All Tasks ===
ID  Status  Title
--  ------  -----
1   [ ]     Buy groceries

Total: 1 task

=== Todo Application ===
[... menu repeats ...]

Select option: 6

Enter task ID to toggle completion: 1

✓ Task marked as complete!

=== Todo Application ===
[... menu repeats ...]

Select option: 0

Thanks for using Todo App! All data will be cleared on exit.
Goodbye!
```

## Development

### Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

### Code Quality

Check code with ruff:

```bash
uv run ruff check src tests
```

Auto-fix issues:

```bash
uv run ruff check --fix src tests
```

Format code:

```bash
uv run ruff format src tests
```

Type checking with mypy:

```bash
uv run mypy src
```

## Project Structure

```
hackathon_todo/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_manager.py  # CRUD operations
│   └── cli/
│       ├── __init__.py
│       ├── menu.py          # Menu and input handling
│       └── display.py       # Output formatting
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_task.py
│   │   └── test_task_manager.py
│   └── integration/
│       ├── __init__.py
│       └── test_cli.py
├── pyproject.toml
└── README.md
```

## Architecture

The application follows a 3-layer architecture:

1. **CLI Layer** (`src/cli/`): User interaction and display
2. **Business Logic Layer** (`src/services/`): Task management operations
3. **Data Model Layer** (`src/models/`): Task entity and validation

## Limitations

- **In-Memory Only**: All data is stored in memory and will be lost when the application exits
- **Single Session**: No persistence between sessions
- **Single User**: Designed for individual use, not multi-user scenarios

## License

This project is part of the Evolution of Todo hackathon - Phase 1.
