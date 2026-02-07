#!/usr/bin/env python3
"""
Test script to verify Hugging Face Spaces compatibility
"""
import os
import sys
import subprocess

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")

    try:
        import fastapi
        print("[OK] FastAPI import successful")
    except ImportError as e:
        print(f"[ERROR] FastAPI import failed: {e}")
        return False

    try:
        import uvicorn
        print("[OK] Uvicorn import successful")
    except ImportError as e:
        print(f"[ERROR] Uvicorn import failed: {e}")
        return False

    try:
        import sqlmodel
        print("[OK] SQLModel import successful")
    except ImportError as e:
        print(f"[ERROR] SQLModel import failed: {e}")
        return False

    try:
        from src.main import app
        print("[OK] Main app import successful")
    except ImportError as e:
        print(f"[ERROR] Main app import failed: {e}")
        return False

    return True

def test_database_config():
    """Test database configuration"""
    print("\n[TEST] Testing database configuration...")

    # Test with SQLite (Hugging Face default)
    os.environ['DATABASE_URL'] = 'sqlite:///./test_todo_app.db'

    try:
        from src.database_hf import create_tables, sync_engine
        print("[OK] Database configuration with SQLite successful")

        # Clean up test database
        if os.path.exists('./test_todo_app.db'):
            os.remove('./test_todo_app.db')

        return True
    except Exception as e:
        print(f"[ERROR] Database configuration failed: {e}")
        return False

def test_app_creation():
    """Test that the app can be created successfully"""
    print("\n[TEST] Testing app creation...")

    try:
        from app import create_app
        app = create_app()
        print("[OK] App creation successful")
        return True
    except Exception as e:
        print(f"[ERROR] App creation failed: {e}")
        return False

def main():
    print("Testing Hugging Face Spaces compatibility...\n")

    tests = [
        test_imports,
        test_database_config,
        test_app_creation
    ]

    all_passed = True
    for test in tests:
        if not test():
            all_passed = False

    print(f"\n{'='*50}")
    if all_passed:
        print("[SUCCESS] All compatibility tests passed!")
        print("Your backend is ready for Hugging Face Spaces deployment.")
    else:
        print("[FAILURE] Some tests failed. Please check the errors above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())