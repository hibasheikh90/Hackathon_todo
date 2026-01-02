# ADR-003: In-Memory Dictionary Storage

> **Scope**: Storage strategy and data structure for task persistence during application runtime.

- **Status:** Accepted
- **Date:** 2026-01-01
- **Feature:** Console Todo Application (001-console-todo-app)
- **Context:** Phase 1 requires task storage during single application session with fast CRUD operations, no persistence between sessions.

<!-- Significance checklist
     1) Impact: YES - Determines performance, scalability, and future migration path
     2) Alternatives: YES - Multiple storage options (list, dict, SQLite, files)
     3) Scope: YES - Affects all CRUD operations, testing strategy, and Phase 2 migration
-->

## Decision

Use **Python dictionary** (`dict[int, Task]`) with **integer keys** for in-memory task storage.

**Implementation Pattern**:
```python
class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}  # {task_id: Task}
        self._next_id: int = 1              # Auto-increment counter

    def add_task(self, title: str, description: str = "") -> Task:
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def list_tasks(self) -> list[Task]:
        # Return newest first
        return sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)
```

**Storage Characteristics**:
- **Data Structure**: Dictionary (hash map)
- **Key**: Integer (task ID)
- **Value**: Task dataclass instance
- **ID Strategy**: Auto-incrementing integer starting at 1
- **Ordering**: Via `created_at` timestamp (newest first)
- **Persistence**: None - data lost on exit (Phase 1 requirement)

## Consequences

### Positive

- **O(1) Lookup**: Get, update, delete by ID in constant time
- **Built-in**: No external dependencies, part of standard library
- **Simple**: Easy to understand and debug
- **Flexible**: Easy iteration, filtering, sorting
- **Memory Efficient**: Minimal overhead for <1000 tasks
- **Type Safe**: `dict[int, Task]` provides full type checking
- **Insertion Order**: Python 3.7+ dicts maintain insertion order (bonus)
- **Fast Development**: No schema setup, migrations, or ORM complexity

### Negative

- **No Persistence**: All data lost on application exit (intentional for Phase 1)
- **Single Session**: Can't share data across multiple app instances
- **Memory Bound**: All tasks must fit in RAM (acceptable for <1000 tasks)
- **No Indexing**: Can't efficiently search by title without full scan
- **No Transactions**: No rollback or atomic operations (not needed for single-user)
- **Migration Required**: Will need migration path for Phase 2 (database)

## Alternatives Considered

### Alternative A: List-Based Storage

```python
self._tasks: list[Task] = []

def get_task(self, task_id: int) -> Optional[Task]:
    for task in self._tasks:
        if task.id == task_id:
            return task
    return None  # O(n) lookup!
```

- **Pros**: Simple, maintains natural order, easy to iterate
- **Cons**: **O(n) lookup by ID**, O(n) delete, slower for 100+ tasks
- **Why Rejected**: Violates performance requirement (<1s for 100 tasks)

### Alternative B: SQLite In-Memory Database

```python
import sqlite3
conn = sqlite3.connect(':memory:')
```

- **Pros**: SQL queries, indexing, familiar for DB developers
- **Cons**: Adds complexity, ORM or manual SQL needed, overkill for simple CRUD
- **Why Rejected**: Unnecessary complexity, violates "minimize dependencies" constraint (conceptually)

### Alternative C: JSON File Storage

```python
import json

def save_tasks(self):
    with open('tasks.json', 'w') as f:
        json.dump([task.to_dict() for task in self._tasks.values()], f)
```

- **Pros**: Persistent storage, simple file format
- **Cons**: **Violates Phase 1 constraint** (must be in-memory only, no persistence)
- **Why Rejected**: Specification explicitly excludes file system persistence

### Alternative D: OrderedDict or defaultdict

```python
from collections import OrderedDict
self._tasks: OrderedDict[int, Task] = OrderedDict()
```

- **Pros**: Maintains insertion order (though regular dict does in 3.7+)
- **Cons**: No real advantage over regular dict in Python 3.13
- **Why Rejected**: Regular `dict` is sufficient and more standard

## Rationale

**Selection Criteria**:
1. **Performance**: O(1) lookup required for <1s operations with 100 tasks
2. **Simplicity**: No external dependencies or complex setup
3. **Phase 1 Constraint**: Must be in-memory only (no persistence)
4. **Type Safety**: Full type hint support with mypy
5. **Future Migration**: Clear path to database in Phase 2

**Why Dictionary Wins**:
- ✅ O(1) get/update/delete by ID
- ✅ Built-in, zero dependencies
- ✅ In-memory only (meets constraint)
- ✅ Excellent type hint support
- ✅ Easy migration to database (similar key-value semantics)

**Performance Validation**:
For 100 tasks:
- Get by ID: O(1) ~0.001ms
- List all: O(n) ~0.1ms (sorting negligible)
- Add task: O(1) ~0.001ms
- Delete: O(1) ~0.001ms

All operations complete in <1ms, well under 1-second requirement.

**Ordering Strategy**:
Instead of relying on insertion order, we explicitly sort by `created_at`:
```python
def list_tasks(self) -> list[Task]:
    return sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)
```
This makes the ordering explicit and testable.

## Implementation Impact

**ID Management**:
- IDs start at 1 (human-friendly)
- Auto-increment on each `add_task()`
- IDs never reused (even after deletion)
- Counter persists for session

**Example State Evolution**:
```python
# Initial state
_tasks = {}
_next_id = 1

# After add_task("Buy milk")
_tasks = {1: Task(id=1, title="Buy milk", ...)}
_next_id = 2

# After add_task("Call dentist"), delete(1), add_task("Finish report")
_tasks = {
    2: Task(id=2, title="Call dentist", ...),
    3: Task(id=3, title="Finish report", ...)
}
_next_id = 4  # Note: ID 1 is not reused
```

**Testing Implications**:
```python
def test_task_retrieval():
    manager = TaskManager()
    task = manager.add_task("Test")

    # O(1) lookup works
    assert manager.get_task(task.id) == task

    # Non-existent ID returns None
    assert manager.get_task(999) is None
```

**Migration Path to Phase 2** (Database):
When adding PostgreSQL in Phase 2:
1. Keep TaskManager interface identical
2. Swap dictionary backend with database queries
3. ID becomes database primary key
4. Code using TaskManager requires no changes

```python
# Phase 2 (pseudocode)
class TaskManager:
    def __init__(self, db_session):
        self._db = db_session  # Replace dict with DB session

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._db.query(Task).filter_by(id=task_id).first()
        # Same interface, different implementation!
```

## Monitoring & Validation

**Success Criteria**:
- All CRUD operations complete in <1ms for 100 tasks
- No memory leaks (tasks properly deleted)
- IDs remain unique across session
- Newest-first ordering works correctly

**Performance Test**:
```python
def test_performance_100_tasks():
    manager = TaskManager()

    # Add 100 tasks
    for i in range(100):
        manager.add_task(f"Task {i}")

    # Measure list operation
    import time
    start = time.time()
    tasks = manager.list_tasks()
    duration = time.time() - start

    assert duration < 0.01  # Should be <10ms
    assert len(tasks) == 100
    assert tasks[0].id > tasks[-1].id  # Newest first
```

## References

- Feature Spec: [specs/001-console-todo-app/spec.md](../../specs/001-console-todo-app/spec.md)
- Data Model: [specs/001-console-todo-app/data-model.md](../../specs/001-console-todo-app/data-model.md#storage-model)
- Research: [specs/001-console-todo-app/research.md](../../specs/001-console-todo-app/research.md#4-in-memory-storage-strategy)
- Related ADRs: ADR-002 (Dataclasses for Task Entity)
- Python Dict Performance: https://wiki.python.org/moin/TimeComplexity
