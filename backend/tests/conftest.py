import sys
import os
from pathlib import Path

# Add the backend directory to the Python path to allow imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set the current working directory to the backend directory
os.chdir(backend_dir)

# Import the app from main.py in the backend root
import sys
sys.path.insert(0, str(backend_dir))  # Make sure backend is in path

# Import models separately to make sure they work
from src.models.user import UserCreate, User, UserRead, UserUpdate, UserLogin
from src.models.task import TaskCreate, Task, TaskRead, TaskUpdate