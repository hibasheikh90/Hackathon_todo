#!/usr/bin/env python3
"""Test script to verify database connection"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from src.database import async_engine

# Load environment variables
load_dotenv()

async def test_db_connection():
    """Test the database connection"""
    try:
        print("Testing database connection...")

        # Test the async engine connection
        async with async_engine.connect() as conn:
            # Execute a simple query
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()

            if row and row.test == 1:
                print("✅ Database connection successful!")
                print(f"✅ Connection returned: {row.test}")
            else:
                print("❌ Database connection failed - unexpected result")

    except Exception as e:
        print(f"❌ Database connection failed with error: {str(e)}")
        return False

    try:
        # Test table creation
        print("\nTesting table creation...")
        from src.database import create_tables
        await create_tables()
        print("✅ Tables created successfully!")

    except Exception as e:
        print(f"❌ Table creation failed with error: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_db_connection())
    if success:
        print("\n🎉 All database tests passed!")
    else:
        print("\n💥 Database tests failed!")
        exit(1)