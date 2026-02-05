@echo off
echo ===============================================
echo RUNNING PHASE 2 TODO APPLICATION
echo ===============================================
echo.
echo IMPORTANT: This application requires Neon PostgreSQL
echo You must have a valid Neon PostgreSQL connection string
echo in your backend/.env file to run this application.
echo.

cd backend

REM Check if we have a Neon connection string
findstr /C:"neon.tech" .env >nul
if errorlevel 1 (
    echo ERROR: No Neon PostgreSQL connection detected in .env
    echo Please update backend/.env with your Neon connection string:
    echo DATABASE_URL=postgresql+asyncpg://username:password@project_id.us-east-1.aws.neon.tech/dbname?sslmode=require
    pause
    exit /b 1
) else (
    echo OK: Neon PostgreSQL configuration detected
)

REM Check if asyncpg is installed
python -c "import asyncpg" >nul 2>&1
if errorlevel 1 (
    echo Installing asyncpg driver...
    pip install asyncpg
) else (
    echo OK: asyncpg driver is installed
)

echo.
echo Starting Backend Server...
echo ---------------------------
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

REM Start the backend
python start_server.py

echo.
echo ===============================================
echo BACKEND STARTED SUCCESSFULLY
echo ===============================================
echo.
echo Now start the frontend in a separate terminal:
echo cd frontend && npm run dev
echo.
echo Frontend will be available at: http://localhost:3000
echo.
pause