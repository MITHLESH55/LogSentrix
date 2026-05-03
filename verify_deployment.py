#!/usr/bin/env python3
"""
LogSentrix PythonAnywhere Deployment Verification Script

This script verifies that all required fixes are in place and tests
the database functionality before going live.

Run this on PythonAnywhere to ensure everything is configured correctly.
"""

import sys
import os
import sqlite3
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_success(text):
    """Print success message."""
    print(f"✅  {text}")

def print_error(text):
    """Print error message."""
    print(f"❌  {text}")

def print_warning(text):
    """Print warning message."""
    print(f"⚠️   {text}")

def print_info(text):
    """Print info message."""
    print(f"ℹ️   {text}")

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print_success(f"{description} exists: {filepath}")
        return True
    else:
        print_error(f"{description} NOT found: {filepath}")
        return False

def check_directory_writable(dirpath, description):
    """Check if a directory is writable."""
    try:
        os.makedirs(dirpath, exist_ok=True)
        test_file = os.path.join(dirpath, ".write_test_" + str(os.getpid()))
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print_success(f"{description} is writable: {dirpath}")
        return True
    except Exception as e:
        print_error(f"{description} is NOT writable: {dirpath}")
        print_error(f"  Error: {e}")
        return False

def test_database_init():
    """Test database initialization."""
    print_header("Testing Database Initialization")
    
    try:
        # Add project to path
        project_path = os.path.dirname(os.path.abspath(__file__))
        if project_path not in sys.path:
            sys.path.insert(0, project_path)
        
        from database import init_db, DB_PATH, get_db_connection
        
        print_info(f"Database path: {DB_PATH}")
        
        # Check if database directory exists or can be created
        db_dir = os.path.dirname(DB_PATH)
        if check_directory_writable(db_dir, "Database directory"):
            # Try to initialize database
            print_info("Attempting to initialize database...")
            init_db()
            print_success("Database initialized successfully!")
            
            # Check if database file exists
            if os.path.exists(DB_PATH):
                print_success(f"Database file created: {DB_PATH}")
                
                # Get file size
                db_size = os.path.getsize(DB_PATH)
                print_info(f"Database file size: {db_size} bytes")
                
                return True
            else:
                print_error(f"Database file NOT created: {DB_PATH}")
                return False
        else:
            return False
            
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_creation():
    """Test user creation."""
    print_header("Testing User Creation")
    
    try:
        project_path = os.path.dirname(os.path.abspath(__file__))
        if project_path not in sys.path:
            sys.path.insert(0, project_path)
        
        from database import create_user, get_user
        from werkzeug.security import generate_password_hash
        
        test_username = "test_deployment_user"
        test_password = "TestPassword123!"
        
        # Check if user already exists
        existing_user = get_user(test_username)
        if existing_user:
            print_warning(f"Test user already exists: {test_username}")
            print_success("✓ User retrieval working correctly")
            return True
        
        # Create test user
        print_info(f"Creating test user: {test_username}")
        hashed_pw = generate_password_hash(test_password)
        result = create_user(test_username, hashed_pw)
        
        if result:
            print_success(f"Test user created: {test_username}")
            
            # Try to retrieve the user
            retrieved_user = get_user(test_username)
            if retrieved_user:
                print_success("✓ User retrieval working correctly")
                return True
            else:
                print_error("Created user cannot be retrieved!")
                return False
        else:
            print_error(f"Failed to create test user: {test_username}")
            return False
            
    except Exception as e:
        print_error(f"User creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """Test Flask app initialization."""
    print_header("Testing Flask App Initialization")
    
    try:
        project_path = os.path.dirname(os.path.abspath(__file__))
        if project_path not in sys.path:
            sys.path.insert(0, project_path)
        
        # Check if app.py can be imported
        print_info("Attempting to import Flask app...")
        from app import app, logger
        
        print_success("Flask app imported successfully")
        
        # Check if logger is configured
        if logger:
            print_success("Logger configured successfully")
        
        # Check if app context is working
        with app.app_context():
            print_success("Flask app context works correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_logging_setup():
    """Check if logging is properly configured."""
    print_header("Checking Logging Setup")
    
    try:
        project_path = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(project_path, "logs")
        
        if check_directory_writable(log_dir, "Logs directory"):
            log_file = os.path.join(log_dir, "app.log")
            
            # Try to write a test log entry
            try:
                with open(log_file, 'a') as f:
                    f.write("[DEPLOYMENT VERIFICATION] Test log entry\n")
                print_success(f"Log file is writable: {log_file}")
                return True
            except Exception as e:
                print_error(f"Cannot write to log file: {e}")
                return False
        else:
            return False
            
    except Exception as e:
        print_error(f"Logging setup check failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("\n")
    print_header("🚀 LogSentrix PythonAnywhere Deployment Verification")
    
    results = {
        "File Structure": check_file_exists("app.py", "app.py"),
        "Database Module": check_file_exists("database.py", "database.py"),
        "Logging Setup": check_logging_setup(),
        "Flask App": test_flask_app(),
        "Database Init": test_database_init(),
        "User Creation": test_user_creation(),
    }
    
    # Print summary
    print_header("📋 Verification Summary")
    
    passed = 0
    failed = 0
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  -  {check_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(results)} checks")
    print("=" * 80)
    
    if failed == 0:
        print_success("All checks passed! ✨")
        print_info("Your PythonAnywhere deployment is ready for production.")
        print_info("\nNext steps:")
        print_info("1. Reload your PythonAnywhere web app")
        print_info("2. Test registration at https://yourusername.pythonanywhere.com/register")
        print_info("3. Monitor logs in: logs/app.log")
        return 0
    else:
        print_error("Some checks failed. Please fix the issues above.")
        print_info("\nFor help, see: PYTHONANYWHERE_DEPLOYMENT_FIX.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
