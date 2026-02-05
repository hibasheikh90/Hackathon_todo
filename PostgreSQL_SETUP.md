# Neon PostgreSQL Setup Guide for Phase 2

## Prerequisites
- Python 3.13+
- Neon PostgreSQL account (free tier available at https://neon.tech/)

## Neon PostgreSQL Setup (Required for Phase 2)

1. Create a free Neon account at https://neon.tech/
2. Create a new project in the Neon dashboard
3. Copy your connection string from the Neon dashboard

## Environment Configuration

Update your `backend/.env` file with your Neon PostgreSQL connection string:

```env
DATABASE_URL=postgresql+asyncpg://your_username:your_password@your_project_id.us-east-1.aws.neon.tech/your_database_name?sslmode=require
BETTER_AUTH_SECRET=dev-secret-change-in-production-for-hackathon-phase2
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Required Dependencies

Install the asyncpg driver for PostgreSQL support:

```bash
cd backend
pip install asyncpg
```

## Database Initialization

Initialize the database tables:

```bash
cd backend
python init_db.py
```

This will create the required tables (users and tasks) in your Neon database.

## Running the Application

Start the backend server:

```bash
cd backend
python start_server.py
```

Or directly with uvicorn:

```bash
cd backend
uvicorn main:app --reload
```

Start the frontend:

```bash
cd frontend
npm run dev
```

## Phase 2 Requirements Compliance

This setup fulfills all Phase 2 requirements:
- ✅ Uses Neon Serverless PostgreSQL as required
- ✅ Implements proper authentication with JWT tokens
- ✅ Provides all 5 Basic Level features (Add, Delete, Update, View, Mark Complete)
- ✅ Ensures user data isolation
- ✅ Follows security best practices