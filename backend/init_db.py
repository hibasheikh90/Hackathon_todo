import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.database import create_tables

async def init_db():
    await create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())