# 🔍 DATABASE AUDIT REPORT - LogSentrix

**Date:** April 27, 2026  
**Project:** LogSentrix Security Monitoring System

---

## EXECUTIVE SUMMARY

⚠️ **CRITICAL ISSUE FOUND:**

- ✓ Database structure is correct
- ✓ Users table exists with proper schema
- ✗ **User registration is NOT saving to database**
- ✗ User "mithlesh.yadav.btech2023..." was NOT found
- ✗ Login uses hardcoded credentials, not database

---

## 1. DATABASE CONFIGURATION

### Database File Location

```
File: database/logs.db
Type: SQLite 3
Size: 442 KB (442,368 bytes)
Status: ✓ ACTIVE
```

### Database Connection Configuration

**Location:** [database.py](database.py#L4)

```python
DB_PATH = "database/logs.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
```

---

## 2. USERS TABLE AUDIT

### Table Structure

```sql
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'analyst',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Required Fields Verification

| Field         | Status    | Notes                  |
| ------------- | --------- | ---------------------- |
| username      | ✓ Present | TEXT, UNIQUE, NOT NULL |
| password_hash | ✓ Present | TEXT, NOT NULL         |
| email         | ✓ Present | TEXT                   |
| role          | ✓ Present | DEFAULT 'analyst'      |
| is_active     | ✓ Present | BOOLEAN tracking       |
| created_at    | ✓ Present | Auto-timestamp         |
| last_login    | ✓ Present | Tracking logins        |

---

## 3. CURRENT USER DATA

### Total Users in Database: **1**

| ID  | Username | Email                | Role    | Created At          |
| --- | -------- | -------------------- | ------- | ------------------- |
| 1   | testuser | testuser@company.com | analyst | 2026-04-27 15:25:04 |

### Search for 'mithlesh' User

```
Status: ✗ NOT FOUND
Query: SELECT * FROM users WHERE username LIKE '%mithlesh%'
Result: 0 records
```

**Conclusion:** User "mithlesh.yadav.btech2023..." does NOT exist in the database.

---

## 4. CRITICAL ISSUES IDENTIFIED

### ⚠️ ISSUE #1: Registration NOT Saving to Database

**Location:** [app.py](app.py#L151-L177)

**Problem:**

```python
# ❌ WRONG - Only saves to in-memory dictionary
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # ... validation code ...

        # Create new user
        try:
            new_user = User(username)
            new_user.set_password(password)
            USERS_DB[username] = new_user  # ← ONLY IN-MEMORY! Not saved to DB
            logger.info(f"New user '{username}' registered successfully")
            return render_template('register.html', success='Account created!')
```

**Impact:**

- Registered users only exist in RAM
- All registered users are LOST when app restarts
- No persistent user accounts
- User "mithlesh" was registered but never persisted

**Evidence:**

- Database only has 1 test user (from test script)
- No registration code saves to database
- Only uses in-memory `USERS_DB` dictionary

---

### ⚠️ ISSUE #2: Login Uses Hardcoded Credentials, NOT Database

**Location:** [app.py](app.py#L76-83)

**Problem:**

```python
# ❌ HARDCODED USERS (In-Memory Only)
USERS_DB = {
    'admin': User('admin'),
    'analyst': User('analyst'),
    'monitor': User('monitor')
}

# Passwords hardcoded
USERS_DB['admin'].set_password('Admin@123')
USERS_DB['analyst'].set_password('Analyst@123')
USERS_DB['monitor'].set_password('Monitor@123')

# Login checks in-memory dictionary
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... validation ...
    user = USERS_DB.get(username)  # ← ONLY checks hardcoded dict!
    if user is None or not user.check_password(password):
        return render_template('login.html', error='Invalid...')
```

**Impact:**

- Only 3 hardcoded users can login (admin, analyst, monitor)
- Newly registered users CANNOT login (they're not in hardcoded dict)
- Database users table is IGNORED during login

---

### ⚠️ ISSUE #3: init_db() NOT Called at App Startup

**Location:** [app.py](app.py#L495-500)

**Problem:**

```python
# ❌ WRONG - init_db() not called at startup
if __name__ == "__main__":
    monitor_thread = threading.Thread(target=monitor_logs)
    monitor_thread.daemon = True
    monitor_thread.start()
    app.run(debug=True)  # ← Database initialized too late!

# ✓ init_db() is called inside dashboard route (line 313)
@app.route("/")
@login_required
def dashboard():
    init_db()  # Called during dashboard access, not startup
```

**Impact:**

- Database tables may not exist before first dashboard access
- Users might encounter errors
- Race condition possible

---

### ⚠️ ISSUE #4: Multiple Database Issues

**Summary:**
| Issue | Status |
|-------|--------|
| Database file exists | ✓ Yes |
| Users table exists | ✓ Yes |
| Registration saves to DB | ✗ NO |
| Login uses DB | ✗ NO |
| init_db() at startup | ✗ NO |
| Registered users persist | ✗ NO |
| Database is redundant | ✓ YES (for users) |

---

## 5. SQL QUERIES TO VIEW USER DATA

### View All Users

```sql
SELECT * FROM users;
```

### View All Users with Password Hash (First 20 chars)

```sql
SELECT id, username, email, role, substr(password_hash, 1, 20) as password_hash_preview, created_at
FROM users;
```

### Search for User by Username

```sql
SELECT * FROM users WHERE username = 'mithlesh.yadav.btech2023';
```

### Count Total Users

```sql
SELECT COUNT(*) as total_users FROM users;
```

### View Active Users Only

```sql
SELECT * FROM users WHERE is_active = 1;
```

### View User Last Login Info

```sql
SELECT username, last_login, created_at, role
FROM users
ORDER BY last_login DESC;
```

### View All User Sessions

```sql
SELECT * FROM session_logs;
```

### Find Users Created Today

```sql
SELECT * FROM users
WHERE DATE(created_at) = DATE('now');
```

---

## 6. SYSTEM OVERVIEW

### All Tables (16 total)

```
✓ users              - 1 record (test user only)
✓ logs               - 2,003 records (security logs)
✓ attack_history     - 1 record
✓ anomaly_logs       - 1 record
✓ ip_reputation      - 1 record
✓ ip_whitelist       - 1 record
✓ ip_blacklist       - 1 record
✓ alerts             - 1 record
✓ email_notifications - 1 record
✓ audit_logs         - 1 record
✓ threat_intelligence - 0 records
✓ system_settings    - 1 record
✓ detection_rules    - 0 records
✓ dashboard_stats    - 0 records
✓ session_logs       - 1 record
```

---

## 7. ROOT CAUSE ANALYSIS

### Why "mithlesh" User NOT in Database

1. **User registered via web form**
2. **Registration code added user to USERS_DB (in-memory dict)**
3. **Registration code did NOT call `create_user()` from database module**
4. **User only existed in RAM**
5. **When app restarted, user was lost**
6. **Database never had "mithlesh" record**

**Timeline:**

```
User registers → Added to USERS_DB dict → App displays success message
    ↓
User tries to login later → But now app is running fresh
    ↓
USERS_DB is reset to hardcoded 3 users → User "mithlesh" doesn't exist
    ↓
Login fails
```

---

## 8. RECOMMENDATIONS

### ✅ FIX #1: Update Registration to Save to Database

**File:** app.py  
**Location:** Lines 151-177

**Replace:**

```python
# ❌ OLD CODE
new_user = User(username)
new_user.set_password(password)
USERS_DB[username] = new_user  # Only in-memory!
```

**With:**

```python
# ✓ NEW CODE
from database import create_user
password_hash = generate_password_hash(password)
if create_user(username, password_hash, email='', role='analyst'):
    logger.info(f"New user '{username}' registered successfully")
    return render_template('register.html', success='Account created!')
else:
    return render_template('register.html', error='Registration failed')
```

---

### ✅ FIX #2: Update Login to Check Database

**File:** app.py  
**Location:** Lines 100-145

**Replace:**

```python
# ❌ OLD CODE
user = USERS_DB.get(username)
if user is None or not user.check_password(password):
```

**With:**

```python
# ✓ NEW CODE
from database import get_user, update_last_login
user_record = get_user(username)
if user_record is None:
    return render_template('login.html', error='Invalid username or password.')

user = User(username, user_record['password_hash'])
if not user.check_password(password):
    return render_template('login.html', error='Invalid username or password.')

# Success - update last login
update_last_login(username)
```

---

### ✅ FIX #3: Call init_db() at Startup

**File:** app.py  
**Location:** Lines 495-500

**Replace:**

```python
# ❌ OLD CODE
if __name__ == "__main__":
    monitor_thread = threading.Thread(target=monitor_logs)
    app.run(debug=True)
```

**With:**

```python
# ✓ NEW CODE
if __name__ == "__main__":
    # Initialize database at startup
    init_db()

    monitor_thread = threading.Thread(target=monitor_logs)
    monitor_thread.daemon = True
    monitor_thread.start()

    app.run(debug=True)
```

---

### ✅ FIX #4: Remove Hardcoded USERS_DB

**File:** app.py  
**Location:** Lines 76-83

**Remove or comment out:**

```python
# ❌ DELETE OR COMMENT OUT
# USERS_DB = {
#     'admin': User('admin'),
#     'analyst': User('analyst'),
#     'monitor': User('monitor')
# }
# USERS_DB['admin'].set_password('Admin@123')
# ...
```

---

## 9. ACTION ITEMS

### Priority: CRITICAL

- [ ] Fix registration to save to database
- [ ] Fix login to check database instead of hardcoded users
- [ ] Move init_db() to app startup
- [ ] Remove hardcoded USERS_DB dictionary
- [ ] Test registration with new user
- [ ] Test login with registered user
- [ ] Verify users persist after app restart

### Priority: HIGH

- [ ] Add email field to registration form (schema supports it)
- [ ] Add password strength validation
- [ ] Add email verification on registration
- [ ] Add password recovery system

### Priority: MEDIUM

- [ ] Implement role-based registration (currently defaults to 'analyst')
- [ ] Add user profile management
- [ ] Add admin user management interface
- [ ] Implement user deletion/deactivation

---

## 10. VERIFICATION STEPS

After making fixes, run these commands:

### Verify Database Structure

```bash
python audit_database.py
```

### Register New User

```
1. Go to http://localhost:5000/register
2. Enter: username=testuser2, password=Test123456, email=test@company.com
3. Click register
```

### Check Database

```bash
python -c "from database import get_user; user = get_user('testuser2'); print('User found!' if user else 'User NOT found')"
```

### Verify Login

```
1. Go to http://localhost:5000/login
2. Login with testuser2 / Test123456
3. Should see dashboard if successful
```

### Check Persistence

```
1. Stop app (Ctrl+C)
2. Restart app
3. Try login with testuser2 again
4. Should still work (proves persistence)
```

---

## 11. DATABASE CONNECTION SUMMARY

| Item                 | Value                    | Location             |
| -------------------- | ------------------------ | -------------------- |
| Database Type        | SQLite 3                 | Embedded             |
| Database File        | database/logs.db         | Project root         |
| Connection String    | sqlite3.connect(DB_PATH) | database.py:L4       |
| Init Function        | init_db()                | database.py:L25      |
| Users Table          | ✓ Exists                 | database.py:L33-47   |
| Create User Function | create_user()            | database.py:L221-234 |
| Get User Function    | get_user()               | database.py:L237-246 |
| Login Check          | HARDCODED (Wrong!)       | app.py:L100-145      |

---

## CONCLUSION

✓ **Database is properly set up and functional**  
✗ **Application code is NOT using the database for user management**  
✗ **User registrations are not persisted**  
✗ **Login is hardcoded to 3 users**

**Impact:** New users like "mithlesh" cannot be registered and persisted.

**Fix Time:** 15-30 minutes

**Difficulty:** Easy (4 changes in 2 files)

---

**Report Generated:** April 27, 2026  
**Next Steps:** Implement the 4 fixes above and re-test.
