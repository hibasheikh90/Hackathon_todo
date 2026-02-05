@echo off
echo ===============================================
echo STARTING TODO APPLICATION FRONTEND
echo ===============================================
echo.

cd frontend

echo Installing frontend dependencies...
npm install

echo.
echo Starting Frontend Server...
echo ---------------------------
echo Frontend will be available at: http://localhost:3000
echo.

npm run dev

echo.
echo ===============================================
echo FRONTEND STARTED SUCCESSFULLY
echo ===============================================
echo.
echo Frontend is now available at: http://localhost:3000
echo.
pause