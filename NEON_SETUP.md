# Neon PostgreSQL Setup for Todo App

This document explains how to set up a Neon PostgreSQL database for the Phase 2 Todo application.

## Prerequisites

- Create a free Neon account at [https://neon.tech/](https://neon.tech/)
- Install the required Python packages: `pip install asyncpg`

## Steps to Create Neon Database

1. **Sign up/Login to Neon**
   - Go to [https://console.neon.tech/](https://console.neon.tech/)
   - Sign up for a free account or log in if you already have one

2. **Create a New Project**
   - Click on "New Project" button
   - Choose a project name (e.g., "todo-app")
   - Select a region closest to your users
   - Click "Create Project"

3. **Get Connection Details**
   - After the project is created, go to the "Connection Details" section
   - You'll see a connection string in the format:
     ```
     postgresql://username:password@ep-xxx-xxxxxx.us-east-1.aws.neon.tech/dbname?sslmode=require
     ```

4. **Update Environment File**
   - Replace the placeholder connection string in `backend/.env` with your actual Neon connection string:
     ```bash
     DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx-xxxxxx.us-east-1.aws.neon.tech/dbname?sslmode=require
     ```

5. **Install Required Dependencies**
   - Make sure you have `asyncpg` installed for async PostgreSQL support:
     ```bash
     pip install asyncpg
     ```

## Testing the Connection

To test the connection to your Neon database:

```bash
# Navigate to the backend directory
cd backend

# Run the database initialization script
python -m init_db
```

## Important Notes

- Neon PostgreSQL offers a generous free tier suitable for development
- The connection string format for SQLAlchemy with asyncpg is: `postgresql+asyncpg://username:password@host/database?sslmode=require`
- Remember to keep your connection string secure and don't commit it to version control
- Neon supports serverless PostgreSQL with smart branching and isolation features

## Critical Setup Step - Database Connection Required!

⚠️ **IMPORTANT**: Before running the application, you MUST update your `backend/.env` file with a valid database connection string. The application will not work with the placeholder values.

### Option 1: Neon PostgreSQL (Required for Phase 2)
After creating your Neon database, update your `backend/.env` file with the actual connection string from your Neon dashboard:

```
DATABASE_URL=postgresql+asyncpg://your_actual_username:your_actual_password@your_project_id.us-east-1.aws.neon.tech/your_database_name?sslmode=require
BETTER_AUTH_SECRET=dev-secret-change-in-production-for-hackathon-phase2
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Option 2: Local PostgreSQL (For Development Only)
If you have a local PostgreSQL instance running:
```
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/todo_app
```

### Option 3: SQLite (For Testing Only)
For quick testing without database setup:
```
DATABASE_URL=sqlite+aiosqlite:///./todo_app.db
```

Then install the required dependencies and run the database initialization:

```bash
cd backend
pip install asyncpg  # if using PostgreSQL (required for Neon)
python -m init_db
```

This will create the necessary tables (users and tasks) in your database.

**Note**: For Phase 2 submission, you must use Neon PostgreSQL as specified in the requirements.