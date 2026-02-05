import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.database import create_tables

async def init_db():
    try:
        await create_tables()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_db())