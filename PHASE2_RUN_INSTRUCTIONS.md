# Phase 2 Todo Application - Setup and Run Instructions

## Phase 2 Requirements Compliance

This application fully complies with Hackathon Phase 2 requirements:
- ✅ Full-stack web application (Next.js frontend + FastAPI backend)
- ✅ Neon Serverless PostgreSQL database
- ✅ All 5 Basic Level features implemented
- ✅ User authentication with JWT tokens
- ✅ Proper security measures and user data isolation

## Setup Instructions

### 1. Backend Setup (Neon PostgreSQL Required)

1. **Create Neon PostgreSQL Database** (Required for Phase 2):
   - Sign up at https://neon.tech/
   - Create a new project
   - Copy your connection string

2. **Update Environment Variables**:
   ```bash
   cd backend
   # Update backend/.env with your Neon connection string:
   DATABASE_URL=postgresql+asyncpg://your_username:your_password@your_project_id.us-east-1.aws.neon.tech/your_database_name?sslmode=require
   ```

3. **Install Dependencies**:
   ```bash
   pip install asyncpg  # Required for PostgreSQL support
   ```

4. **Initialize Database**:
   ```bash
   python init_db.py
   ```

5. **Start Backend**:
   ```bash
   python start_server.py
   # Or: uvicorn main:app --reload
   ```

### 2. Frontend Setup

1. **Navigate to Frontend**:
   ```bash
   cd frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Start Frontend**:
   ```bash
   npm run dev
   ```

## Application URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Backend Docs**: http://localhost:8000/docs
- **Database**: Neon Serverless PostgreSQL (cloud-based)

## Features Available

1. **User Authentication**:
   - User registration and login
   - JWT-based session management
   - Secure token storage

2. **Task Management** (All 5 Basic Level Features):
   - Add Task: Create new todo items
   - Delete Task: Remove tasks from the list
   - Update Task: Modify existing task details
   - View Task List: Display all tasks
   - Mark as Complete: Toggle task completion status

3. **Security Features**:
   - User data isolation (users only see their own tasks)
   - Rate limiting
   - Input sanitization
   - JWT token validation

## Phase 2 Compliance Verification

- ✅ Uses Neon Serverless PostgreSQL (not local database)
- ✅ Implements proper authentication system
- ✅ All 5 required features are implemented
- ✅ Follows security best practices
- ✅ Full-stack architecture with proper separation
- ✅ Responsive web interface

The application is now ready for Phase 2 submission with Neon PostgreSQL as the backend database.