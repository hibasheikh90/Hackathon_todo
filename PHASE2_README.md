# Phase 2: Full-Stack Web Application with Neon PostgreSQL

## Overview

This Phase 2 implementation transforms the console application into a modern full-stack web application with persistent storage using Neon Serverless PostgreSQL database. The application follows the requirements specified in the Hackathon II project.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Spec-Driven | Claude Code + Spec-Kit Plus |
| Authentication | Better Auth |

## Database Schema

### Tables

#### users
- id: UUID (primary key)
- email: string (unique, not null)
- password_hash: string (not null)
- created_at: timestamp
- updated_at: timestamp
- is_active: boolean (default true)

#### tasks
- id: UUID (primary key)
- user_id: UUID (foreign key -> users.id)
- title: string (not null, 1-255 characters)
- description: text (nullable, max 10,000 characters)
- is_completed: boolean (default false)
- created_at: timestamp
- updated_at: timestamp

## API Endpoints

All endpoints require a valid JWT token in the Authorization header: `Authorization: Bearer <token>`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | List all tasks for the authenticated user |
| POST | /api/tasks | Create a new task for the authenticated user |
| GET | /api/tasks/{task_id} | Get a specific task |
| PUT | /api/tasks/{task_id} | Update a task |
| DELETE | /api/tasks/{task_id} | Delete a task |
| PATCH | /api/tasks/{task_id}/complete | Toggle completion status |

## Setup Instructions

### 1. Create Neon PostgreSQL Database

1. Sign up at [https://neon.tech/](https://neon.tech/)
2. Create a new project
3. Get your connection string from the Neon dashboard

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install asyncpg
   ```

3. Update the `.env` file with your Neon database connection string:
   ```
   DATABASE_URL=postgresql+asyncpg://your_username:your_password@your_project_id.us-east-1.aws.neon.tech/your_database_name?sslmode=require
   BETTER_AUTH_SECRET=your_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. Initialize the database tables:
   ```bash
   python -m init_db
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

⚠️ **CRITICAL**: The application will not work until you replace the placeholder values in the `DATABASE_URL` with your actual Neon PostgreSQL credentials. If you encounter connection errors, verify that:
- You have created a Neon PostgreSQL database
- Your connection string is properly formatted
- You have installed asyncpg: `pip install asyncpg`
- Your Neon database allows connections from your network

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Ensure the `.env.local` file has the correct backend API URL:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
   ```

4. Start the frontend:
   ```bash
   npm run dev
   ```

## Authentication Flow

1. User logs in via Better Auth on the frontend
2. Better Auth creates a JWT token with user information
3. Frontend includes the JWT token in the Authorization header for API requests
4. Backend verifies the JWT token and extracts user ID
5. Backend filters all data access by the authenticated user's ID

## Security Features

- JWT-based authentication with token expiration
- Input sanitization middleware
- Rate limiting (30 requests/minute for read, 20/minute for write)
- SQL injection prevention via SQLModel/SQLAlchemy
- User isolation - users can only access their own data
- Password hashing with bcrypt

## Testing

The backend includes comprehensive error handling and security logging:

- Data access attempts are logged
- Failed authentication attempts are logged
- Ownership violations are logged
- API rate limits are enforced

## Key Features Implemented

✅ All 5 Basic Level features:
- Add Task – Create new todo items
- Delete Task – Remove tasks from the list
- Update Task – Modify existing task details
- View Task List – Display all tasks
- Mark as Complete – Toggle task completion status

✅ Authentication – User signup/signin using Better Auth
✅ RESTful API endpoints
✅ Responsive frontend interface
✅ Neon Serverless PostgreSQL database storage
✅ JWT-based authentication with user isolation

## Architecture Benefits

- **User Isolation**: Each user only sees their own tasks
- ** Stateless Auth**: Backend doesn't need to call frontend to verify users
- **Token Expiry**: JWTs expire automatically (configurable)
- **No Shared DB Session**: Frontend and backend can verify auth independently

This implementation satisfies all Phase 2 requirements with a robust, secure, and scalable architecture.