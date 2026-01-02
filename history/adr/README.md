# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the Console Todo Application project.

## What is an ADR?

An ADR documents a significant architectural decision along with its context and consequences. ADRs help teams understand:
- **Why** a decision was made
- **What** alternatives were considered
- **What** trade-offs were accepted

## Index

### Active ADRs

| ID | Title | Status | Date | Feature |
|----|-------|--------|------|---------|
| [001](./001-python-313-uv-package-manager.md) | Python 3.13 and UV Package Manager | Accepted | 2026-01-01 | 001-console-todo-app |
| [002](./002-dataclasses-for-task-entity.md) | Python Dataclasses for Task Entity | Accepted | 2026-01-01 | 001-console-todo-app |
| [003](./003-in-memory-dictionary-storage.md) | In-Memory Dictionary Storage | Accepted | 2026-01-01 | 001-console-todo-app |

### Superseded ADRs

None yet.

### Rejected ADRs

None yet.

## When to Create an ADR

Create an ADR when a decision meets ALL three criteria:

1. **Impact**: Has long-term consequences for architecture, platform, security, or data model
2. **Alternatives**: Multiple viable options were considered with different trade-offs
3. **Scope**: Affects multiple components or is a cross-cutting concern

Examples of ADR-worthy decisions:
- Technology stack selection (framework, language, database)
- Authentication/authorization approach
- Data storage strategy
- API design patterns
- Deployment architecture

Examples of decisions that DON'T need ADRs:
- Naming conventions
- Code style choices
- Individual library selections for isolated features
- Temporary workarounds

## ADR Template

See `.specify/templates/adr-template.md` for the standard ADR format.

## Creating a New ADR

Use the `/sp.adr <decision-title>` command to generate a new ADR automatically.

Manual process:
1. Determine next available ID number
2. Copy ADR template
3. Name file: `###-kebab-case-title.md`
4. Fill in all sections
5. Update this README index
6. Reference from implementation plan

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Thoughtworks Technology Radar on ADRs](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
