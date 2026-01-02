# ADR-002: Python Dataclasses for Task Entity

> **Scope**: Data modeling approach for the Task entity and future domain objects.

- **Status:** Accepted
- **Date:** 2026-01-01
- **Feature:** Console Todo Application (001-console-todo-app)
- **Context:** Need to represent Task entities with validation, type safety, and clean syntax while avoiding external dependencies.

<!-- Significance checklist
     1) Impact: YES - Defines data modeling pattern for entire application and future phases
     2) Alternatives: YES - Multiple options (plain classes, namedtuples, Pydantic, attrs)
     3) Scope: YES - Affects all entity definitions, testing, serialization strategy
-->

## Decision

Use **Python dataclasses** (stdlib `@dataclass` decorator) for all domain entities, starting with the Task entity.

**Implementation Pattern**:
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate attributes after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title must be 200 characters or less")
        if len(self.description) > 2000:
            raise ValueError("Description must be 2000 characters or less")
```

## Consequences

### Positive

- **Zero Dependencies**: Part of Python standard library (since 3.7)
- **Type Hints**: Native support for type annotations, excellent mypy integration
- **Auto-Generated Methods**: Automatic `__init__`, `__repr__`, `__eq__`, `__hash__`
- **Default Values**: Clean syntax for optional fields with defaults
- **Validation Hook**: `__post_init__` allows validation logic post-initialization
- **Immutability Option**: `frozen=True` parameter for immutable objects (if needed)
- **Field Metadata**: `field()` function supports default factories, metadata, repr control
- **Readability**: Concise, declarative syntax - easy to understand at a glance
- **Testing**: Auto-generated `__eq__` makes assertion comparisons simple
- **IDE Support**: Excellent autocompletion and type inference in modern IDEs

### Negative

- **No Built-in Validation**: Requires manual validation in `__post_init__` or methods
- **No Serialization**: Need custom `to_dict()` / `from_dict()` for JSON (Phase 2+)
- **Limited Constraints**: Can't enforce constraints like "positive integer" at type level
- **Mutable by Default**: Objects are mutable unless explicitly frozen
- **Inheritance Quirks**: Can be tricky with complex inheritance hierarchies
- **No Automatic Coercion**: Won't auto-convert types (e.g., string to int)

## Alternatives Considered

### Alternative A: Plain Python Classes

```python
class Task:
    def __init__(self, id: int, title: str, description: str = "", completed: bool = False):
        self.id = id
        self.title = title
        # ... manual boilerplate
```

- **Pros**: Maximum control, no "magic", explicit
- **Cons**: Lots of boilerplate (`__init__`, `__repr__`, `__eq__`), error-prone
- **Why Rejected**: Unnecessary boilerplate for simple data containers

### Alternative B: NamedTuple

```python
from typing import NamedTuple

class Task(NamedTuple):
    id: int
    title: str
    description: str = ""
    completed: bool = False
```

- **Pros**: Immutable, lightweight, tuple-like behavior
- **Cons**: Immutable by default (need new instance for updates), harder to add methods/validation
- **Why Rejected**: Mutability needed for toggle_complete() and update operations

### Alternative C: Pydantic Models

```python
from pydantic import BaseModel, field_validator

class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    completed: bool = False

    @field_validator('title')
    def validate_title(cls, v):
        if len(v) > 200:
            raise ValueError('Title too long')
        return v
```

- **Pros**: Excellent validation, automatic JSON serialization, type coercion
- **Cons**: **External dependency** (violates constraint), heavier weight, overkill for simple case
- **Why Rejected**: Constraint specifies "minimize external dependencies" - Pydantic adds ~5MB

### Alternative D: attrs Library

```python
from attrs import define, field

@define
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
```

- **Pros**: More features than dataclasses, excellent validation, mature library
- **Cons**: **External dependency** (violates constraint), more to learn
- **Why Rejected**: Dataclasses provide sufficient features, attrs unnecessary

## Rationale

**Selection Criteria**:
1. **No External Dependencies** (hard constraint from spec)
2. **Type Safety** (mypy integration essential)
3. **Validation Support** (title/description length limits)
4. **Mutability** (need toggle_complete and update operations)
5. **Clean Syntax** (readability and maintainability)

**Why Dataclasses Win**:
- ✅ Meets all 5 criteria
- ✅ Part of standard library (no dependency)
- ✅ Validation via `__post_init__` is sufficient for our needs
- ✅ Mutable by default (perfect for our use case)
- ✅ Most Pythonic approach for data modeling in modern Python

**Validation Strategy**:
For Phase 1, manual validation in `__post_init__` is adequate:
- Only 2 validation rules (title not empty, max lengths)
- Clear error messages via ValueError
- No complex schemas or nested validation needed

For Phase 2+ (with API/database), can add:
- `to_dict()` method for JSON serialization
- `from_dict()` classmethod for deserialization
- Or migrate to Pydantic if external dependency constraint is relaxed

## Implementation Impact

**File Structure**:
```
src/models/
├── __init__.py
└── task.py          # Task dataclass + validation
```

**Testing Implications**:
```python
# Easy equality comparison
def test_task_equality():
    task1 = Task(id=1, title="Test")
    task2 = Task(id=1, title="Test")
    assert task1 == task2  # Auto-generated __eq__

# Easy representation in test output
def test_repr():
    task = Task(id=1, title="Test")
    print(task)  # Task(id=1, title='Test', ...)
```

**Future Extension**:
When serialization needed (Phase 2):
```python
@dataclass
class Task:
    # ... existing code ...

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        # Parse and create Task from dict
        ...
```

## Monitoring & Validation

**Success Criteria**:
- All Task instances pass validation on creation
- No runtime type errors (mypy catches all type issues)
- Tests use equality comparison without custom comparators
- Code reviews confirm readability and maintainability

**Migration Path** (if needed):
If Pydantic becomes necessary (Phase 2+ with API):
1. Add Pydantic as dependency
2. Inherit from both `BaseModel` and keep `@dataclass`
3. Or create Pydantic schemas separate from domain entities (layered approach)

## References

- Feature Spec: [specs/001-console-todo-app/spec.md](../../specs/001-console-todo-app/spec.md)
- Data Model: [specs/001-console-todo-app/data-model.md](../../specs/001-console-todo-app/data-model.md)
- Research: [specs/001-console-todo-app/research.md](../../specs/001-console-todo-app/research.md#3-data-modeling-approach)
- Related ADRs: ADR-001 (Python 3.13)
- Python Dataclasses Docs: https://docs.python.org/3/library/dataclasses.html
- PEP 557: https://peps.python.org/pep-0557/
