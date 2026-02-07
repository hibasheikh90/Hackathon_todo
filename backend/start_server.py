#!/usr/bin/env python3
"""Simple server startup script with explicit environment configuration for Hugging Face Spaces"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set default environment variables if not set in .env
# Use SQLite as default for Hugging Face Spaces compatibility
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'sqlite:///./todo_app.db'
if not os.getenv('BETTER_AUTH_SECRET'):
    os.environ['BETTER_AUTH_SECRET'] = 'dev-secret-change-in-production-for-hackathon-phase2'
if not os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'):
    os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

# Start the server using uvicorn
if __name__ == "__main__":
    try:
        # Import and start the server
        import uvicorn
        from main import app

        print("Starting server with database configuration:", os.getenv('DATABASE_URL'))
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)
    except ImportError:
        # If direct import doesn't work, try using subprocess
        print("Starting server with subprocess...")
        result = subprocess.run([sys.executable, "-c", """
import os
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///./todo_app.db')
os.environ['BETTER_AUTH_SECRET'] = 'dev-secret-change-in-production-for-hackathon-phase2'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

import uvicorn
import sys
sys.path.insert(0, './src')
import main
uvicorn.run('main:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), reload=False)
"""], cwd=os.getcwd())