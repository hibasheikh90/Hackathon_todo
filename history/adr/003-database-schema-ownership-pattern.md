# ADR-003: Database Schema & Ownership Pattern

**Status**: Accepted
**Date**: 2026-01-31
**Deciders**: Engineering Team

## Context

We need to design a database schema for our todo application that properly separates user data and ensures users can only access their own tasks. The schema must support efficient querying while maintaining data integrity and security.

## Decision

We will use SQLModel to define User and Task models with a foreign key relationship (User 1 → N Tasks). We will enforce ownership at both the database level (via foreign key constraints) and application level (via ownership checks in FastAPI endpoints). Queries will always filter by the current user's ID.

## Rationale

- **Data Integrity**: Foreign key constraints ensure referential integrity at the database level
- **Performance**: Proper indexing on user_id enables efficient ownership queries
- **Security**: Dual-layer protection (database and application) minimizes data leakage risk
- **Scalability**: Efficient queries with proper indexing support growth
- **Maintainability**: Clear ownership pattern makes code easier to understand and maintain

## Approach

1. **Database Schema**:
   - User table with id (UUID, PK), email (unique), password_hash, timestamps
   - Task table with id (UUID, PK), title, description, is_completed, user_id (FK to User.id), timestamps
   - Index on Task.user_id for efficient ownership queries

2. **Application Logic**:
   - All task queries filtered by current user's ID
   - Ownership verification in FastAPI dependencies before processing requests
   - Error responses when users attempt to access others' data

3. **Query Patterns**:
   - Always include WHERE clause filtering by user_id
   - Use JOINs when necessary but ensure user isolation
   - Implement proper pagination for large datasets

## Schema Definition

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_users_email ON users(email);
```

## Consequences

### Positive
- Strong data integrity through foreign key constraints
- Efficient queries with proper indexing
- Clear separation of user data
- Compliance with privacy requirements
- Scalable to large number of users

### Negative
- Additional complexity in queries requiring user_id filtering
- Potential performance impact of ownership checks
- Need for careful handling of user deletion scenarios
- More complex joins when aggregating data

## Alternatives Considered

1. **Separate Tables Per User**: Would create maintenance complexity and wasn't scalable
2. **No Ownership Enforcement**: Would violate security requirements completely
3. **Application-Only Enforcement**: Would be vulnerable to direct database access
4. **Row-Level Security**: More complex to implement than needed for this application