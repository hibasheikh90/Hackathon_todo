# Quickstart Guide: Full-Stack Todo Web Application

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- PostgreSQL-compatible database (Neon recommended)
- Git
- Package managers: npm/yarn and pip/uv

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Environment Configuration

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
JWT_SECRET=another-secret-for-additional-security
NEON_DATABASE_URL=your-neon-postgres-connection-string
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install

# Create environment file
cp .env.example .env.local
```

Edit the `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

### 3. Database Initialization

```bash
# From backend directory
cd backend

# Initialize database tables
python -m scripts.init_db

# Or if using alembic for migrations
alembic upgrade head
```

### 4. Running the Applications

#### Backend (FastAPI)
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload --port 8000
```

#### Frontend (Next.js)
```bash
cd frontend
npm run dev
# or
yarn dev
```

### 5. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Backend Docs: http://localhost:8000/docs

## Development Commands

### Backend Commands
```bash
# Run tests
cd backend
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

### Frontend Commands
```bash
# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Run linting
npm run lint

# Format code
npm run format
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### Task Management
- `GET /api/tasks` - Get current user's tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/toggle` - Toggle task completion

## Troubleshooting

### Common Issues

#### Database Connection
- Ensure PostgreSQL/Neon is running and accessible
- Verify DATABASE_URL in backend .env file
- Check that database tables have been created

#### Authentication Problems
- Confirm BETTER_AUTH_SECRET is the same in frontend and backend
- Ensure JWT configuration matches between services
- Check that CORS settings allow cross-origin requests

#### Frontend-Backend Communication
- Verify NEXT_PUBLIC_API_URL points to the correct backend URL
- Confirm backend is running when frontend makes API requests
- Check browser console for CORS or network errors

### Development Tips
- Both services need to be running simultaneously for full functionality
- Backend changes require restart unless using --reload flag
- Frontend hot-reloads automatically on file changes
- Check both backend and frontend logs for error messages