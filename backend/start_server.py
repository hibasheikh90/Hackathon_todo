#!/usr/bin/env python3
"""Simple server startup script with explicit environment configuration"""

import os
import sys
import subprocess

# Set the environment variable before starting the server
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./todo_app.db'
os.environ['BETTER_AUTH_SECRET'] = 'dev-secret-change-in-production-for-hackathon-phase2'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

# Start the server using uvicorn
if __name__ == "__main__":
    try:
        # Import and start the server
        import uvicorn
        from backend.main import app

        print("Starting server with SQLite configuration...")
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
    except ImportError:
        # If direct import doesn't work, try using subprocess
        print("Starting server with subprocess...")
        result = subprocess.run([sys.executable, "-c", """
import os
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./todo_app.db'
os.environ['BETTER_AUTH_SECRET'] = 'dev-secret-change-in-production-for-hackathon-phase2'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

import uvicorn
import sys
sys.path.insert(0, './backend/src')
import backend.main
uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=False)
"""], cwd=os.getcwd())