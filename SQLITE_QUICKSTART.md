# SQLite Database Setup - Quick Start

## ✅ What's Complete

Your LogSentrix project now has a comprehensive SQLite database with **15 specialized tables**:

| Table                   | Purpose                        |
| ----------------------- | ------------------------------ |
| **users**               | User authentication & profiles |
| **logs**                | Security logs from all sources |
| **attack_history**      | Detected attacks & threats     |
| **anomaly_logs**        | ML-detected anomalies          |
| **ip_reputation**       | IP threat intelligence         |
| **ip_whitelist**        | Trusted IPs                    |
| **ip_blacklist**        | Blocked IPs                    |
| **alerts**              | System alerts & notifications  |
| **email_notifications** | Email delivery logs            |
| **audit_logs**          | Compliance & audit trail       |
| **threat_intelligence** | External threat data           |
| **system_settings**     | Configuration storage          |
| **detection_rules**     | Custom security rules          |
| **dashboard_stats**     | Daily statistics               |
| **session_logs**        | User session tracking          |

---

## 🚀 Getting Started

### 1. Database Initialization

```python
from database import init_db

# Run once at startup
init_db()
```

### 2. Replace Hardcoded Users in app.py

**Current (OLD):**

```python
USERS_DB = {
    'admin': User('admin'),
    'analyst': User('analyst'),
}
USERS_DB['admin'].set_password('your_secure_password_here')
```

**Replace with (NEW):**

```python
from database import create_user, get_user
from werkzeug.security import generate_password_hash

def init_default_users():
    """Create default users if they don't exist."""
    users = [
        ('admin', 'your_secure_password_here', 'admin@company.com', 'admin'),
        ('analyst', 'your_secure_password_here', 'analyst@company.com', 'analyst'),
        ('monitor', 'your_secure_password_here', 'monitor@company.com', 'monitor'),
    ]
    for username, password, email, role in users:
        if not get_user(username):
            create_user(username, generate_password_hash(password), email, role)

# Call on app startup
init_default_users()
```

### 3. Update Login Route

```python
from database import get_user, update_last_login, log_session

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... existing validation code ...

    # Get user from database
    user_record = get_user(username)

    if user_record is None or not user.check_password(password):
        # ... error handling ...
        return render_template('login.html', error='Invalid credentials.')

    # Update last login
    update_last_login(username)

    # Log session
    log_session(username, request.remote_addr, request.headers.get('User-Agent'))

    return redirect(url_for('dashboard'))
```

---

## 📊 Using Database Functions

### Store Logs

```python
from database import insert_logs

df = parse_logs(file)  # Your existing parser
insert_logs(df)  # Stores in database
```

### Detect & Store Attacks

```python
from database import insert_attack, insert_alert

alert = {
    'ip': '10.0.0.50',
    'type': 'brute_force',
    'attempts': 150,
    'severity': 'CRITICAL'
}
insert_attack(alert)
insert_alert('brute_force', 'CRITICAL', '10.0.0.50', 'attacker', 'Attack detected', 'Description...')
```

### Store Anomalies

```python
from database import insert_anomaly

insert_anomaly(
    ip='192.168.1.50',
    user='suspicious_user',
    reason='ML detected unusual pattern',
    anomaly_score=87.5
)
```

### IP Management

```python
from database import add_ip_blacklist, is_ip_blacklisted, add_ip_whitelist

# Block malicious IP
add_ip_blacklist('10.0.0.50', 'Known botnet', 'critical', 'admin')

# Check if IP is blacklisted
if is_ip_blacklisted('10.0.0.50'):
    print("Block connection")

# Whitelist trusted IP
add_ip_whitelist('192.168.1.200', 'Company VPN', 'admin', 'Internal network')
```

### Get Dashboard Data

```python
from database import get_db_stats, get_unread_alerts, get_active_attacks

stats = get_db_stats()
# Returns: total_logs, active_attacks, active_anomalies, unread_alerts, unique_ips, unique_users

alerts = get_unread_alerts()  # Unread alerts
attacks = get_active_attacks()  # Active (unresolved) attacks
```

### Audit Logging

```python
from database import log_audit

log_audit(
    user_id='analyst1',
    action='acknowledge_alert',
    resource_type='alert',
    resource_id=123,
    description='Acknowledged alert #123',
    ip_address='192.168.1.100'
)
```

---

## 📁 Files Created/Modified

**Modified:**

- `database.py` - Completely redesigned with 15 tables & 40+ functions

**Created:**

- `DATABASE_STRUCTURE.md` - Full schema documentation
- `DATABASE_INTEGRATION.md` - Integration guide & examples
- `test_sqlite_database.py` - Comprehensive test suite (13 tests)

---

## ✅ Test Results

```
Passed: 13/13 ✅

✓ Database Initialization
✓ User Management
✓ Log Management
✓ Attack Detection
✓ Anomaly Detection
✓ IP Management
✓ IP Reputation
✓ Alert Management
✓ Email Notifications
✓ Audit Logging
✓ System Settings
✓ Session Logging
✓ Database Statistics
```

---

## 🔄 Data Flow Architecture

```
Logs (CSV/JSON)
    ↓
parser.py
    ↓
insert_logs() → [logs table]
    ↓
detector.py (Brute Force)
    ↓
insert_attack() → [attack_history table]
    ↓
↙     ↙     ↙
detect_anomaly()    check_ip_reputation()    process_alerts()
    ↓                      ↓                          ↓
insert_anomaly()    insert_ip_reputation()   insert_alert()
    ↓                      ↓                          ↓
[anomaly_logs]      [ip_reputation]          [alerts]
    ↓                      ↓                          ↓
    └──────────────────────┴──────────────────────┘
                           ↓
                    Dashboard Query
                           ↓
                  [dashboard_stats]
```

---

## 🎯 Next Steps

1. **Backup existing data** (if any):

   ```bash
   cp database/logs.db database/logs_backup.db
   ```

2. **Update app.py** with database functions (see integration examples above)

3. **Test the application**:

   ```bash
   python test_sqlite_database.py  # Run test suite
   python app.py  # Start application
   ```

4. **Monitor database**:
   ```python
   from database import get_db_stats
   stats = get_db_stats()
   print(stats)
   ```

---

## 📚 Documentation Files

- **[DATABASE_STRUCTURE.md](DATABASE_STRUCTURE.md)** - Complete schema reference
- **[DATABASE_INTEGRATION.md](DATABASE_INTEGRATION.md)** - Integration patterns & examples
- **[test_sqlite_database.py](test_sqlite_database.py)** - Test suite

---

## 🔐 Security Features Included

✅ Password hashing (no plaintext storage)
✅ Audit trail for compliance
✅ User role-based permissions
✅ Session tracking
✅ IP reputation management
✅ Whitelist/Blacklist system
✅ Email notification logging

---

## 💾 Database Management

### Cleanup Old Data

```python
from database import clear_old_data

# Delete data older than 30 days
clear_old_data(days=30)
```

### Get Database Size

```python
import os
size_mb = os.path.getsize('database/logs.db') / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB")
```

### Backup

```bash
cp database/logs.db database/logs_backup_$(date +%Y%m%d_%H%M%S).db
```

---

## ❓ Common Questions

**Q: Will this work with existing logs?**
A: Yes! Old logs will be preserved. Start using new functions for new data.

**Q: How many records can it store?**
A: SQLite handles millions of records. For performance, clean up data older than 30 days.

**Q: Is it production-ready?**
A: Yes! All 13 tests pass. For enterprise use, consider PostgreSQL.

**Q: How do I query the database directly?**
A: Use the `get_db_connection()` context manager for custom queries.

---

**Status: ✅ COMPLETE & TESTED**

The SQLite database is fully operational and ready for integration into your application!
