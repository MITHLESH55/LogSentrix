# PythonAnywhere Deployment Fix - LogSentrix Registration Issue

## Summary of Changes

This document outlines all fixes applied to resolve registration failures on PythonAnywhere.

---

## 1. Database Path Resolution ✅

### Problem

The original code used a relative path: `DB_PATH = "database/logs.db"`

- On PythonAnywhere, the working directory may differ from expectations
- Database directory might not exist or be unwritable

### Fix Applied (database.py)

```python
def get_db_path():
    """Get absolute database path for PythonAnywhere compatibility."""
    base_dir = Path(__file__).resolve().parent
    db_dir = base_dir / "database"
    return str(db_dir / "logs.db")

DB_PATH = get_db_path()
```

**Benefits:**

- ✅ Absolute path resolution
- ✅ Works regardless of working directory
- ✅ Compatible with all deployment environments

---

## 2. Database Connection Enhancements ✅

### Problem

- No directory existence checks
- No write permission verification
- No timeout handling for slow connections

### Fix Applied (database.py)

```python
@contextmanager
def get_db_connection():
    """Context manager for database connections with PythonAnywhere support."""
    db_dir = os.path.dirname(DB_PATH)

    # Ensure database directory exists
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, mode=0o755, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create database directory '{db_dir}': {e}")

    # Check write permissions
    if not os.access(os.path.dirname(DB_PATH), os.W_OK):
        raise RuntimeError(f"No write permission for database directory: {db_dir}")

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)  # Timeout for PythonAnywhere
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Database connection error: {e}")
    finally:
        conn.close()
```

**Benefits:**

- ✅ Auto-creates database directory
- ✅ Validates write permissions upfront
- ✅ 10-second timeout for unreliable connections
- ✅ Foreign key support for data integrity

---

## 3. Database Initialization on Startup ✅

### Problem

- `init_db()` was imported but never called
- Database tables didn't exist on deployment
- No error feedback if initialization failed

### Fix Applied (app.py)

```python
def init_app_database():
    """Initialize database when Flask app starts."""
    try:
        logger.info("=" * 80)
        logger.info("🚀 LogSentrix Starting Up")
        logger.info("=" * 80)
        init_db()
        logger.info("✅ Database initialization completed successfully")
        return True
    except Exception as e:
        logger.critical(f"❌ CRITICAL: Database initialization failed: {e}", exc_info=True)
        print(f"[CRITICAL] Database initialization failed: {e}")
        return False

# Initialize database on app startup
with app.app_context():
    if not init_app_database():
        logger.error("Continuing with uninitialized database. Registration will fail.")
```

**Benefits:**

- ✅ Automatic database creation on app start
- ✅ Comprehensive error logging
- ✅ App context properly configured
- ✅ Clear visibility of initialization status

---

## 4. Improved Logging System ✅

### Problem

- Limited debugging information
- Errors weren't persisted
- No log file for PythonAnywhere troubleshooting

### Fix Applied (app.py)

```python
def setup_logging():
    """Configure logging for better error tracking."""
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

logger = setup_logging()
```

**Benefits:**

- ✅ Debug-level logging for detailed tracking
- ✅ Logs written to `logs/app.log` (persistent)
- ✅ Dual output: file + stdout
- ✅ Clear timestamp and log levels

---

## 5. Enhanced Registration Error Handling ✅

### Problem

- Generic "An error occurred" message
- No exception details logged
- Silent failures on database issues

### Fix Applied (app.py - /register route)

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with detailed error logging."""

    # ... validation checks ...

    try:
        logger.info(f"Attempting to register new user: {username} from {request.remote_addr}")
        hashed_pw = generate_password_hash(password)
        result = create_user(username, hashed_pw)

        if result:
            logger.info(f"✅ User registration successful: {username}")
            return render_template('register.html', success='Account created successfully!'), 200
        else:
            logger.warning(f"User creation returned False for: {username}")
            return render_template('register.html', error='Username already exists...'), 400

    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error during registration of '{username}': {e}", exc_info=True)
        return render_template('register.html', error='Username already exists...'), 400
    except RuntimeError as e:
        logger.error(f"Runtime error during user creation: {e}", exc_info=True)
        return render_template('register.html', error=f'Database error: {str(e)}'), 500
    except Exception as e:
        logger.error(f"Unexpected error registering user {username}: {type(e).__name__}: {e}", exc_info=True)
        return render_template('register.html', error='An unexpected error occurred...'), 500
```

**Benefits:**

- ✅ Detailed error logging with full stack traces
- ✅ Specific error type handling
- ✅ User receives helpful error messages
- ✅ Admins can diagnose via logs

---

## 6. Enhanced create_user Function ✅

### Problem

- Silent failures with minimal error info
- Didn't distinguish between different failure types
- Generic exception handling

### Fix Applied (database.py)

```python
def create_user(username, password_hash, email=None, role='analyst'):
    """Create a new user with comprehensive error handling."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO users(username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
            """, (username, password_hash, email, role))
            conn.commit()
            print(f"[DB] ✅ User created: {username}")
            return True
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"[DB] ⚠️  User already exists: {username}")
            return False
        raise
    except sqlite3.OperationalError as e:
        print(f"[DB ERROR] ❌ Database operational error for user '{username}': {e}")
        raise RuntimeError(f"Database error: {e}")
    except Exception as e:
        print(f"[DB ERROR] ❌ Failed to create user '{username}': {type(e).__name__}: {e}")
        raise
```

**Benefits:**

- ✅ Distinguishes between user-exists and database errors
- ✅ Informative error messages
- ✅ Proper exception propagation for debugging

---

## Deployment Checklist for PythonAnywhere

### Step 1: Upload Latest Code

- [ ] Push changes to GitHub
- [ ] Pull latest code on PythonAnywhere

### Step 2: Verify Directory Permissions

```bash
# SSH into PythonAnywhere console:
cd /home/yourusername/LogSentrix
ls -la database/
chmod 755 database/
```

### Step 3: Verify Web App Configuration

In PythonAnywhere Web App settings:

- [ ] Source code: `/home/yourusername/LogSentrix`
- [ ] Python version: 3.8 or later
- [ ] Virtual environment: `/home/yourusername/.virtualenvs/logsent`

### Step 4: Check WSGI Configuration

Your WSGI file should look like:

```python
# /var/www/yourusername_pythonanywhere_com_wsgi.py

import sys
import os

path = '/home/yourusername/LogSentrix'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)
from app import app as application
```

### Step 5: Reload Web App

- [ ] Go to Web tab
- [ ] Click "Reload yourusername.pythonanywhere.com"

### Step 6: Monitor Logs

- [ ] Check `/home/yourusername/LogSentrix/logs/app.log`
- [ ] Check PythonAnywhere error log: Web → Error log

### Step 7: Test Registration

1. Visit your app URL
2. Click Register
3. Try creating an account
4. Check logs for detailed output

---

## Debugging: How to Find Errors

### View Application Logs

```bash
# SSH into PythonAnywhere:
tail -f /home/yourusername/LogSentrix/logs/app.log
```

### View PythonAnywhere Error Log

- Go to Web tab → Error log
- Scroll to bottom for latest errors

### Common Issues & Solutions

#### Issue: "No write permission for database directory"

**Solution:**

```bash
mkdir -p /home/yourusername/LogSentrix/database
chmod 755 /home/yourusername/LogSentrix/database
```

#### Issue: "Failed to create database directory"

**Solution:**

- Check parent directory exists: `/home/yourusername/LogSentrix`
- Verify permissions on LogSentrix folder
- May need PythonAnywhere support if permission denied

#### Issue: "Database file locked"

**Solution:**

- Check database timeout in connection string
- Restart web app
- May indicate concurrent access issues

#### Issue: "UNIQUE constraint failed: users.username"

**Solution:**

- This is expected - user already exists
- Try registering with different username

---

## Verification Commands

Run these to verify everything is working:

```python
# Test from PythonAnywhere console
import sys
sys.path.insert(0, '/home/yourusername/LogSentrix')

from database import DB_PATH, init_db, create_user, get_user
from werkzeug.security import generate_password_hash

# Check database path
print(f"Database path: {DB_PATH}")

# Initialize database
print("Initializing database...")
init_db()

# Test user creation
print("Creating test user...")
hashed_pw = generate_password_hash("TestPass123!")
result = create_user("testuser123", hashed_pw)
print(f"User creation result: {result}")

# Test user retrieval
print("Retrieving test user...")
user = get_user("testuser123")
print(f"User found: {user is not None}")
```

---

## Performance Optimization for PythonAnywhere

### 1. Use PythonAnywhere's Cron Feature

For periodic tasks like log cleanup:

```bash
0 2 * * * python /home/yourusername/LogSentrix/cleanup.py
```

### 2. Enable Caching

Add to app.py:

```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
```

### 3. Monitor Resource Usage

- Go to Web tab → View usage
- Keep an eye on CPU time and disk usage

---

## Testing Registration Locally

Before deployment, test locally:

```bash
# Set Flask environment
export FLASK_ENV=development
export FLASK_APP=app.py

# Run tests
python test_sqlite_database.py

# Run app locally
python app.py

# In browser: http://localhost:5000/register
```

---

## Files Modified

1. **database.py**
   - Added `get_db_path()` function
   - Enhanced `get_db_connection()` with permission checks
   - Updated `init_db()` with try-except
   - Improved `create_user()` error handling

2. **app.py**
   - Added `setup_logging()` function
   - Added `init_app_database()` function
   - Enhanced `/register` route with detailed logging
   - Added sqlite3 import

---

## Next Steps

1. ✅ Deploy these changes to PythonAnywhere
2. ✅ Reload web app
3. ✅ Test registration
4. ✅ Monitor `/home/yourusername/LogSentrix/logs/app.log`
5. ✅ Once working, consider adding:
   - Email verification for registrations
   - Rate limiting on registration attempts
   - Admin dashboard for user management
   - Database backup automation

---

## Support

If registration still fails after these fixes:

1. **Check logs first:**

   ```bash
   tail -50 /home/yourusername/LogSentrix/logs/app.log
   ```

2. **Verify database file exists:**

   ```bash
   ls -la /home/yourusername/LogSentrix/database/logs.db
   ```

3. **Check PythonAnywhere error log:**
   - Web tab → Error log (bottom of page)

4. **Restart web app:**
   - Web tab → Reload button

---

**Last Updated:** 2026-05-03
**Status:** ✅ Production Ready
