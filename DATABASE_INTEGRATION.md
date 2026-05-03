# SQLite Integration Guide - LogSentrix

## Quick Setup

### Step 1: Initialize Database

Add this to your app startup (in `app.py`):

```python
from database import init_db

# Initialize database on first run
init_db()
```

### Step 2: Update app.py to Use New Database Functions

#### Replace User Management (Hardcoded Users)

**Before:**

```python
# Hardcoded users (OLD - DO NOT USE)
USERS_DB = {
    'admin': User('admin'),
    'analyst': User('analyst'),
    'monitor': User('monitor')
}
USERS_DB['admin'].set_password('your_secure_password_here')
```

**After:**

```python
from database import create_user, get_user, update_last_login
from werkzeug.security import generate_password_hash

# Initialize users on first run (optional)
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

#### Update Login Route

```python
from database import get_user, update_last_login, log_session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Get user from database
        user_record = get_user(username)

        if user_record is None or not User(username, user_record['password_hash']).check_password(password):
            logger.warning(f"Failed login for '{username}' from {request.remote_addr}")
            return render_template('login.html', error='Invalid credentials.'), 401

        # Create User object
        user = User(username, user_record['password_hash'])
        login_user(user)

        # Update last login
        update_last_login(username)

        # Log session
        log_session(username, request.remote_addr, request.headers.get('User-Agent'))

        logger.info(f"User '{username}' logged in from {request.remote_addr}")
        return redirect(url_for('dashboard'))

    return render_template('login.html')
```

---

## Integration Points

### 1. Log Processing Integration

**File:** `parser.py` → `app.py` → `database.py`

```python
from parser import parse_logs
from database import insert_logs, log_audit

@app.route('/api/upload-logs', methods=['POST'])
def upload_logs():
    """Upload and parse log files."""
    if not current_user.is_authenticated:
        return {"error": "Unauthorized"}, 401

    file = request.files['file']

    # Parse logs
    df = parse_logs(file)

    # Store in database
    insert_logs(df)

    # Log action for audit trail
    log_audit(
        current_user.username,
        'upload_logs',
        'file',
        None,
        f"Uploaded {len(df)} logs",
        request.remote_addr
    )

    return {"message": "Logs stored successfully", "count": len(df)}
```

---

### 2. Threat Detection Integration

**File:** `detector.py` → `database.py`

```python
from detector import detect_bruteforce
from database import insert_attack, insert_alert, get_ip_reputation, is_ip_blacklisted

def process_detections(df):
    """Process threats and store in database."""

    # Detect brute force attacks
    attacks = detect_bruteforce(df)

    for attack in attacks:
        ip = attack['ip']

        # Check if IP is blacklisted
        if is_ip_blacklisted(ip):
            attack['severity'] = 'CRITICAL'

        # Get IP reputation
        reputation = get_ip_reputation(ip)
        if reputation and reputation['threat_level'] == 'critical':
            attack['severity'] = 'CRITICAL'

        # Store attack
        attack_id = insert_attack(attack)

        # Create alert
        insert_alert(
            alert_type='brute_force',
            severity=attack['severity'],
            ip=ip,
            user=attack.get('user'),
            title=f"{attack['attack_type']} detected from {ip}",
            description=f"Attack attempts: {attack['attempts']}"
        )
```

---

### 3. Anomaly Detection Integration

**File:** `ai_detector.py` → `database.py`

```python
from ai_detector import detect_anomaly
from database import insert_anomaly, insert_alert

def process_anomalies(df):
    """Process anomalies and store in database."""

    # Detect anomalies
    anomalies = detect_anomaly(df)

    for idx, row in anomalies.iterrows():
        # Store anomaly
        insert_anomaly(
            ip=row['ip'],
            user=row['user'],
            reason='Machine Learning detected unusual pattern',
            anomaly_score=row.get('anomaly_score', 50)
        )

        # Create alert
        insert_alert(
            alert_type='anomaly',
            severity='MEDIUM',
            ip=row['ip'],
            user=row['user'],
            title=f"Anomalous activity from {row['user']}",
            description=f"Anomaly score: {row.get('anomaly_score', 'N/A')}"
        )
```

---

### 4. Dashboard Integration

**File:** `app.py` → `database.py`

```python
from database import (
    get_db_stats,
    get_unread_alerts,
    get_active_attacks,
    get_active_anomalies,
    get_recent_logs
)

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    """Get dashboard statistics."""

    stats = get_db_stats()
    recent_alerts = get_unread_alerts()
    active_attacks = get_active_attacks()
    active_anomalies = get_active_anomalies()
    recent_logs = get_recent_logs(limit=50)

    return jsonify({
        'stats': stats,
        'alerts': [dict(alert) for alert in recent_alerts],
        'attacks': [dict(attack) for attack in active_attacks],
        'anomalies': [dict(anomaly) for anomaly in active_anomalies],
        'recent_logs': [dict(log) for log in recent_logs]
    })
```

---

### 5. IP Management Integration

**File:** `ip_lookup.py` → `database.py`

```python
from database import (
    insert_ip_reputation,
    add_ip_whitelist,
    add_ip_blacklist,
    is_ip_whitelisted,
    is_ip_blacklisted
)

def process_ip_reputation(ip):
    """Check and store IP reputation."""

    # Don't process whitelisted IPs
    if is_ip_whitelisted(ip):
        return

    # Check reputation from external service
    reputation = check_ip_reputation(ip)

    # Store reputation
    insert_ip_reputation(
        ip=ip,
        reputation=reputation['status'],
        threat_level=reputation['threat_level'],
        source='AbuseIPDB'
    )

    # Auto-blacklist if malicious
    if reputation['threat_level'] == 'critical':
        add_ip_blacklist(
            ip=ip,
            reason=f"High abuse score: {reputation['abuse_score']}",
            severity='critical',
            added_by='system'
        )
```

---

### 6. Email Alerts Integration

**File:** `alerts.py` → `database.py`

```python
from database import insert_alert, insert_email_notification, mark_email_sent
import threading

def process_alerts(alerts):
    """Process and send email alerts."""

    for alert in alerts:
        # Create alert record
        alert_id = insert_alert(
            alert_type=alert.get('type'),
            severity=alert.get('severity'),
            ip=alert.get('ip'),
            user=alert.get('user'),
            title=alert.get('title'),
            description=alert.get('description')
        )

        # Create email notification record
        email_id = insert_email_notification(
            recipient_email=RECEIVER_EMAIL,
            subject=f"🚨 {alert.get('severity')} ALERT: {alert.get('title')}",
            message=alert.get('description'),
            alert_id=alert_id
        )

        # Send email in background
        def send_email_thread():
            try:
                send_email_alert(
                    subject=f"🚨 {alert.get('severity')} ALERT",
                    message=alert.get('description')
                )
                mark_email_sent(email_id)
            except Exception as e:
                print(f"[ERROR] Email send failed: {e}")

        thread = threading.Thread(target=send_email_thread)
        thread.daemon = True
        thread.start()
```

---

### 7. Audit Trail Integration

**File:** `app.py` - All routes

```python
from database import log_audit

# Example: Log when analyst acknowledges an alert
@app.route('/api/alert/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_alert(alert_id):
    """Acknowledge an alert."""

    # Perform action
    mark_alert_acknowledged(alert_id, current_user.username)

    # Log action
    log_audit(
        user_id=current_user.username,
        action='acknowledge_alert',
        resource_type='alert',
        resource_id=alert_id,
        description=f"Acknowledged alert #{alert_id}",
        ip_address=request.remote_addr
    )

    return jsonify({"message": "Alert acknowledged"})
```

---

## API Endpoints - New Database Functions

### Dashboard Statistics

```
GET /api/dashboard-data
Returns: stats, alerts, attacks, anomalies, logs
```

### IP Management

```
POST /api/ip/whitelist
Body: {"ip": "192.168.1.100", "reason": "Company VPN"}

POST /api/ip/blacklist
Body: {"ip": "10.0.0.50", "reason": "Malicious", "severity": "high"}

GET /api/ip/<ip>/reputation
Returns: IP reputation data
```

### Alert Management

```
GET /api/alerts/unread
Returns: All unread alerts

POST /api/alerts/<id>/read
Marks alert as read

POST /api/alerts/<id>/acknowledge
Marks alert as acknowledged by analyst
```

### User Management

```
GET /api/users
Returns: All users

POST /api/users
Body: {"username": "new_user", "email": "...", "role": "analyst"}

POST /api/users/<id>/reset-password
```

---

## Testing the Integration

### Test Script

Create `test_database.py`:

```python
from database import *
from werkzeug.security import generate_password_hash

def test_database():
    """Test all database functions."""

    print("[TEST] Initializing database...")
    init_db()

    print("[TEST] Creating user...")
    create_user('testuser', generate_password_hash('test123'), 'test@company.com')
    user = get_user('testuser')
    assert user is not None
    print("✓ User creation works")

    print("[TEST] Testing IP management...")
    add_ip_whitelist('192.168.1.100', 'Test IP', 'admin', 'Testing')
    assert is_ip_whitelisted('192.168.1.100')
    print("✓ Whitelist works")

    print("[TEST] Testing alerts...")
    alert_id = insert_alert('test', 'HIGH', '10.0.0.1', 'testuser', 'Test Alert', 'Testing')
    assert alert_id is not None
    unread = get_unread_alerts()
    assert len(unread) > 0
    print("✓ Alerts work")

    print("[TEST] Testing audit logs...")
    log_audit('testuser', 'test_action', 'test_resource', 1, 'Testing', '127.0.0.1')
    print("✓ Audit logging works")

    print("[TEST] Getting stats...")
    stats = get_db_stats()
    print(f"✓ Database stats: {stats}")

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_database()
```

Run with:

```bash
python test_database.py
```

---

## Performance Optimization

### 1. Query Optimization

```python
# ❌ Slow - No index
SELECT * FROM logs WHERE user = ?

# ✅ Fast - Indexed
SELECT * FROM logs WHERE ip = ?  # Has index
```

### 2. Batch Operations

```python
# ❌ Slow - Multiple inserts
for row in df.iterrows():
    insert_logs(row)

# ✅ Fast - Batch insert
insert_logs(df)
```

### 3. Connection Pooling

```python
# Already implemented with context manager
with get_db_connection() as conn:
    # Automatic cleanup
    pass
```

---

## Deployment Checklist

- [ ] Run `init_db()` on first deployment
- [ ] Create default users with strong passwords
- [ ] Enable email notifications
- [ ] Configure IP lookup service
- [ ] Set up automated backups
- [ ] Monitor database size
- [ ] Schedule `clear_old_data()` cleanup
- [ ] Test all API endpoints
- [ ] Enable audit logging
- [ ] Document any custom rules

---

## Common Tasks

### Backup Database

```python
import shutil
from datetime import datetime

backup_name = f"logs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy('database/logs.db', f'database/backups/{backup_name}')
```

### Export Alerts to CSV

```python
import pandas as pd
from database import get_unread_alerts

alerts = get_unread_alerts()
df = pd.DataFrame([dict(a) for a in alerts])
df.to_csv('alerts.csv', index=False)
```

### Reset Dashboard Stats

```python
from database import get_db_connection

with get_db_connection() as conn:
    c = conn.cursor()
    c.execute("DELETE FROM dashboard_stats")
    conn.commit()
```

---

## Troubleshooting

### "Database is locked"

```python
# Solution: Ensure proper connection cleanup
with get_db_connection() as conn:
    # Always use context manager
    pass
```

### "Column not found"

- Verify table exists: `init_db()`
- Check column names in schema
- Ensure database file is current version

### Slow queries

- Check if indexes exist
- Use `EXPLAIN QUERY PLAN` to analyze
- Consider archiving old data

---

For more details, see [DATABASE_STRUCTURE.md](DATABASE_STRUCTURE.md)
