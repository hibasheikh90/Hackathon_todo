# ADR-001: Python 3.13 and UV Package Manager

> **Scope**: Runtime and package management cluster - groups language version, package manager, and virtual environment strategy.

- **Status:** Accepted
- **Date:** 2026-01-01
- **Feature:** Console Todo Application (001-console-todo-app)
- **Context:** Phase 1 implementation requires selecting a Python version and package management strategy for fast, reliable dependency management and development workflow.

<!-- Significance checklist
     1) Impact: YES - Determines development workflow, performance, and future compatibility
     2) Alternatives: YES - Multiple package managers available (pip, Poetry, PDM, UV)
     3) Scope: YES - Affects all developers, CI/CD, and entire project lifecycle
-->

## Decision

Use **Python 3.13+** as the target runtime with **UV** as the package manager.

**Stack Components**:
- **Language**: Python 3.13+ (latest stable version)
- **Package Manager**: UV (https://github.com/astral-sh/uv)
- **Environment**: UV-managed virtual environments
- **Lock File**: `uv.lock` for dependency reproducibility
- **Project Config**: `pyproject.toml` (PEP 518 standard)

## Consequences

### Positive

- **Performance**: UV is 10-100x faster than pip for dependency resolution and installation
- **Modern Features**: Python 3.13 includes latest performance improvements and type hint enhancements
- **Simplicity**: UV combines package management and virtual environment in one tool
- **Lock File**: Deterministic builds with `uv.lock`, no version drift
- **Future-Proof**: Latest Python version ensures long-term support and modern features
- **Cross-Platform**: Consistent behavior across Windows, macOS, and Linux
- **Standard Library**: Python 3.13 std lib rich enough to avoid external dependencies for core features
- **Fast Development Cycle**: UV's speed reduces friction during development

### Negative

- **UV Adoption**: Relatively new tool (2023), smaller community than pip/Poetry
- **Breaking Changes**: Python 3.13 deprecates some older patterns, may require updates
- **Requirement**: Users must install Python 3.13+ (not default on many systems yet)
- **Learning Curve**: Developers familiar with pip/Poetry need to learn UV commands
- **Windows Path Length**: Python on Windows can hit MAX_PATH (260 char) limits (mitigated by modern Windows 10+)

## Alternatives Considered

### Alternative A: Python 3.11 + pip + venv

- **Pros**: Most widely used, mature ecosystem, no new tool learning
- **Cons**: Much slower dependency resolution, manual venv management, no lock file by default
- **Why Rejected**: Performance penalty adds up during development, missing modern Python features

### Alternative B: Python 3.12 + Poetry

- **Pros**: Excellent dependency management, mature tool, lock file support
- **Cons**: Slower than UV, heavier weight, adds complexity for simple project
- **Why Rejected**: UV provides same benefits with better performance

### Alternative C: Python 3.13 + PDM

- **Pros**: Modern, PEP 582 support, good performance
- **Cons**: Less established than UV, smaller community
- **Why Rejected**: UV has better momentum and speed benchmarks

### Alternative D: Python 3.10 + pip-tools

- **Pros**: Lightweight, pip-compatible, lock file via requirements.txt
- **Cons**: Older Python version, slower, multi-tool setup (pip + pip-tools)
- **Why Rejected**: Missing Python 3.13 features and UV's integrated workflow

## Rationale

**Why Python 3.13?**
1. Latest performance optimizations (PEP 709 inlined comprehensions)
2. Enhanced type system for better mypy integration
3. Future-proof: ensures support for 5+ years
4. Constraint explicitly specified in project requirements

**Why UV?**
1. **Speed**: 10-100x faster than pip eliminates development friction
2. **Simplicity**: Single tool for packages + environments
3. **Determinism**: `uv.lock` ensures reproducible builds
4. **Modern**: Built in Rust, designed for Python 3.7+
5. **Constraint**: Explicitly specified in project requirements

**Trade-off Assessment**:
The benefits (speed, simplicity, modern features) outweigh the risks (new tool, bleeding edge Python). For a greenfield project with no legacy constraints, using the latest stable tools is optimal.

## Implementation Impact

**Developer Workflow**:
```bash
# Install UV once
curl -LsSf https://astral.sh/uv/install.sh | sh

# Project setup
uv sync                    # Create venv + install dependencies
uv run python -m src.main  # Run application
uv run pytest              # Run tests
uv pip install <package>   # Add dependency
```

**CI/CD Changes**:
- GitHub Actions: Use `astral-sh/setup-uv` action
- Install time: ~5-10 seconds (vs ~60s with pip)
- Caching: UV lock file enables aggressive caching

**Documentation Updates**:
- README.md: UV installation instructions
- quickstart.md: UV commands instead of pip
- Contributing guide: UV workflow

## Monitoring & Validation

**Success Criteria**:
- Dependency installation completes in <10 seconds
- All developers can set up environment in <2 minutes
- No version conflicts across team members (lock file works)

**Rollback Plan**:
If UV causes blocking issues:
1. Create `requirements.txt` from `pyproject.toml`
2. Switch to `pip install -r requirements.txt`
3. Minimal code changes needed (pyproject.toml still works with pip)

## References

- Feature Spec: [specs/001-console-todo-app/spec.md](../../specs/001-console-todo-app/spec.md)
- Implementation Plan: [specs/001-console-todo-app/plan.md](../../specs/001-console-todo-app/plan.md)
- Research: [specs/001-console-todo-app/research.md](../../specs/001-console-todo-app/research.md#2-package-management)
- Related ADRs: None (first ADR for this feature)
- UV Documentation: https://github.com/astral-sh/uv
- Python 3.13 Release Notes: https://docs.python.org/3.13/whatsnew/3.13.html
