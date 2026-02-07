# Todo API Backend for Hugging Face Spaces

This is a FastAPI-based Todo application backend designed for deployment on Hugging Face Spaces.

## Features

- FastAPI framework for high-performance API
- User authentication system
- Task management functionality
- Rate limiting and input sanitization
- Database support (SQLite for Hugging Face Spaces, PostgreSQL for production)

## Environment Variables

The following environment variables should be configured in your Hugging Face Space settings:

- `DATABASE_URL`: Database connection string (defaults to SQLite for Spaces)
- `BETTER_AUTH_SECRET`: Secret key for JWT token signing
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

## Deployment on Hugging Face Spaces

This repository is configured for easy deployment on Hugging Face Spaces with Docker. The Dockerfile and space.yaml files are already set up for deployment.

## API Endpoints

- `GET /` - Health check endpoint
- `/api/auth/*` - Authentication endpoints
- `/api/tasks/*` - Task management endpoints

## Local Development

To run locally:

```bash
pip install -r requirements.txt
python start_server.py
```

The server will be available at http://localhost:8000