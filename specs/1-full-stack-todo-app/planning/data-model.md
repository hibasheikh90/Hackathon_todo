# Data Model: Full-Stack Todo Web Application

## Entity Definitions

### User Entity
**Description**: Represents an authenticated user in the system

**Fields**:
- `id`: UUID (Primary Key, Required)
  - Unique identifier for the user
  - Auto-generated using UUID4
- `email`: String (Required, Unique, Indexed)
  - User's email address for authentication
  - Max length: 255 characters
  - Format: Valid email pattern
- `password_hash`: String (Required)
  - Hashed password using bcrypt or similar
  - Max length: 255 characters
- `created_at`: DateTime (Required)
  - Timestamp of account creation
  - Auto-generated on creation
- `updated_at`: DateTime (Required)
  - Timestamp of last account update
  - Auto-updated on modification
- `is_active`: Boolean (Required, Default: True)
  - Whether the account is active/enabled

**Constraints**:
- Email must be unique across all users
- Email format must be valid
- Password must be hashed (never stored in plaintext)

### Task Entity
**Description**: Represents a todo item owned by a specific user

**Fields**:
- `id`: UUID (Primary Key, Required)
  - Unique identifier for the task
  - Auto-generated using UUID4
- `title`: String (Required, Indexed)
  - Brief title of the task
  - Min length: 1 character
  - Max length: 255 characters
- `description`: Text (Optional)
  - Detailed description of the task
  - Max length: 10,000 characters
- `is_completed`: Boolean (Required, Default: False)
  - Whether the task has been completed
- `created_at`: DateTime (Required)
  - Timestamp of task creation
  - Auto-generated on creation
- `updated_at`: DateTime (Required)
  - Timestamp of last task update
  - Auto-updated on modification
- `user_id`: UUID (Foreign Key, Required, Indexed)
  - Reference to the owning user
  - Links to User.id

**Constraints**:
- Title must be 1-255 characters
- user_id must reference an existing User
- Users can only access tasks where task.user_id equals their user.id

## Relationships

### User → Tasks (One-to-Many)
- One User can own many Tasks
- Foreign Key: Task.user_id → User.id
- Index: On Task.user_id for efficient querying
- Action on User deletion: [To be determined - soft delete vs cascade]

## Validation Rules

### User Validation
- Email format: Must match standard email pattern
- Password strength: Minimum 8 characters, with uppercase, lowercase, and number
- Email uniqueness: No duplicate email addresses allowed
- Active status: Inactive users cannot access the system

### Task Validation
- Title required: Must not be empty or whitespace-only
- Title length: 1-255 characters
- Description length: Up to 10,000 characters
- User ownership: Tasks can only be accessed by their owner
- Completion status: Boolean value only

## State Transitions

### Task Completion
- `is_completed: false` → `is_completed: true` (when user marks as complete)
- `is_completed: true` → `is_completed: false` (when user unmarks as complete)

### User Activation
- `is_active: true` → `is_active: false` (account deactivation)
- `is_active: false` → `is_active: true` (account reactivation)

## Indexes

### Required Indexes
- User.email (unique)
- Task.user_id (foreign key, for efficient ownership queries)
- Task.is_completed (for filtering completed/incomplete tasks)
- User.created_at (for account age queries)
- Task.created_at (for chronological sorting)

## Access Control

### Ownership Rules
- Users can only CREATE tasks for themselves
- Users can only READ tasks they own
- Users can only UPDATE tasks they own
- Users can only DELETE tasks they own
- Admin users (if any) may have additional permissions (to be defined)

## Audit Trail
- created_at and updated_at timestamps on all entities
- User actions may be logged separately for security purposes