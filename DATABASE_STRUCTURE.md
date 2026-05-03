# SQLite Database Structure - LogSentrix

## Overview

The enhanced SQLite database structure for LogSentrix separates all data types into specialized tables with proper relationships, indexing, and management functions.

---

## Database Tables

### 1. **USERS Table**

Stores user account information and authentication data.

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

**Columns:**

- `id` - Unique user identifier
- `username` - Unique username (login)
- `password_hash` - Hashed password (never plain text)
- `email` - User email address
- `role` - User role (admin, analyst, monitor)
- `is_active` - Account status
- `created_at` - Account creation time
- `last_login` - Last login timestamp
- `last_updated` - Profile update timestamp

**Related Functions:**

```python
create_user(username, password_hash, email, role)
get_user(username)
update_last_login(username)
```

---

### 2. **LOGS Table**

Stores all parsed security logs from various sources.

```sql
CREATE TABLE logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL,
    status TEXT NOT NULL,
    user TEXT NOT NULL,
    ip TEXT NOT NULL,
    source_file TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**

- `id` - Log entry ID
- `time` - Log timestamp
- `status` - Login status (SUCCESS, FAILED)
- `user` - Username attempting login
- `ip` - Source IP address
- `source_file` - Log file source
- `created_at` - Database insertion time

**Indexes:**

- `idx_logs_ip` - Fast lookup by IP
- `idx_logs_user` - Fast lookup by user
- `idx_logs_time` - Time-based queries

**Related Functions:**

```python
insert_logs(df)
get_recent_logs(limit=100)
```

---

### 3. **ATTACK_HISTORY Table**

Stores detected security attacks and threats.

```sql
CREATE TABLE attack_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    attack_type TEXT NOT NULL,
    attempts INTEGER DEFAULT 1,
    severity TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    resolved_by TEXT
)
```

**Columns:**

- `id` - Attack record ID
- `ip` - Attacking IP address
- `attack_type` - Type of attack (brute-force, etc.)
- `attempts` - Number of attempts
- `severity` - CRITICAL, HIGH, MEDIUM, LOW
- `description` - Attack details
- `status` - open or resolved
- `timestamp` - Detection time
- `resolved_at` - Time marked as resolved
- `resolved_by` - Analyst who resolved it

**Indexes:**

- `idx_attack_history_ip` - Find attacks by IP
- `idx_attack_history_severity` - Filter by severity

**Related Functions:**

```python
insert_attack(alert)
get_active_attacks()
resolve_attack(attack_id, resolved_by)
```

---

### 4. **ANOMALY_LOGS Table**

Stores detected anomalous behaviors using ML algorithms.

```sql
CREATE TABLE anomaly_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    user TEXT NOT NULL,
    reason TEXT NOT NULL,
    anomaly_score REAL,
    features TEXT,
    status TEXT DEFAULT 'open',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
)
```

**Columns:**

- `id` - Anomaly record ID
- `ip` - Source IP
- `user` - Associated user
- `reason` - Why flagged as anomaly
- `anomaly_score` - ML confidence score (0-100)
- `features` - JSON features used in detection
- `status` - open or resolved
- `timestamp` - Detection time
- `resolved_at` - Resolution time

**Related Functions:**

```python
insert_anomaly(ip, user, reason, anomaly_score)
get_active_anomalies()
```

---

### 5. **IP_REPUTATION Table**

Stores IP reputation data from threat intelligence sources.

```sql
CREATE TABLE ip_reputation(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL PRIMARY KEY,
    reputation TEXT NOT NULL,
    threat_level TEXT,
    abuse_reports INTEGER DEFAULT 0,
    blacklist_count INTEGER DEFAULT 0,
    last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT
)
```

**Columns:**

- `ip` - IP address (unique)
- `reputation` - good, suspicious, malicious
- `threat_level` - low, medium, high, critical
- `abuse_reports` - Number of abuse reports
- `blacklist_count` - Times blacklisted
- `last_checked` - Last verification time
- `updated_at` - Last update time
- `source` - Data source (AbuseIPDB, etc.)

**Related Functions:**

```python
insert_ip_reputation(ip, reputation, threat_level, source)
get_ip_reputation(ip)
```

---

### 6. **IP_WHITELIST Table**

Stores trusted IP addresses that should not trigger alerts.

```sql
CREATE TABLE ip_whitelist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL,
    description TEXT,
    added_by TEXT,
    reason TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
)
```

**Columns:**

- `ip` - Whitelisted IP
- `description` - Why trusted (e.g., "Company VPN")
- `added_by` - Who added it
- `reason` - Business reason
- `is_active` - Current status
- `created_at` - Addition time
- `expires_at` - Optional expiration

**Related Functions:**

```python
add_ip_whitelist(ip, description, added_by, reason)
is_ip_whitelisted(ip)
```

---

### 7. **IP_BLACKLIST Table**

Stores IPs that should be blocked or closely monitored.

```sql
CREATE TABLE ip_blacklist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL,
    reason TEXT NOT NULL,
    severity TEXT DEFAULT 'high',
    added_by TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    block_duration INTEGER
)
```

**Columns:**

- `ip` - Blacklisted IP
- `reason` - Why blocked
- `severity` - Block level (low, medium, high, critical)
- `added_by` - Who added it
- `is_active` - Current status
- `created_at` - Addition time
- `expires_at` - Optional expiration
- `block_duration` - Duration in minutes (optional)

**Related Functions:**

```python
add_ip_blacklist(ip, reason, severity, added_by, block_duration)
is_ip_blacklisted(ip)
```

---

### 8. **ALERTS Table**

Stores all system alerts and notifications.

```sql
CREATE TABLE alerts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    ip TEXT NOT NULL,
    user TEXT,
    title TEXT NOT NULL,
    description TEXT,
    is_read BOOLEAN DEFAULT 0,
    is_acknowledged BOOLEAN DEFAULT 0,
    acknowledged_by TEXT,
    acknowledged_at DATETIME,
    action_taken TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
)
```

**Columns:**

- `id` - Alert ID
- `alert_type` - Type (brute_force, anomaly, etc.)
- `severity` - CRITICAL, HIGH, MEDIUM, LOW
- `ip` - Associated IP
- `user` - Associated user
- `title` - Alert title
- `description` - Full description
- `is_read` - Read status
- `is_acknowledged` - Analyst acknowledgment
- `acknowledged_by` - Who acknowledged it
- `acknowledged_at` - Time acknowledged
- `action_taken` - Response action
- `created_at` - Alert time
- `resolved_at` - Resolution time

**Related Functions:**

```python
insert_alert(alert_type, severity, ip, user, title, description)
get_unread_alerts()
mark_alert_read(alert_id)
```

---

### 9. **EMAIL_NOTIFICATIONS Table**

Logs all email alerts sent to analysts.

```sql
CREATE TABLE email_notifications(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    alert_id INTEGER,
    status TEXT DEFAULT 'pending',
    sent_at DATETIME,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(alert_id) REFERENCES alerts(id)
)
```

**Columns:**

- `id` - Notification ID
- `recipient_email` - Email address
- `subject` - Email subject
- `message` - Email content
- `alert_id` - Link to alert
- `status` - pending, sent, failed
- `sent_at` - Send time
- `error_message` - Error details if failed
- `created_at` - Creation time

**Related Functions:**

```python
insert_email_notification(recipient_email, subject, message, alert_id)
mark_email_sent(email_id)
```

---

### 10. **AUDIT_LOGS Table**

Compliance and audit trail for all user actions.

```sql
CREATE TABLE audit_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id INTEGER,
    description TEXT,
    ip_address TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**

- `id` - Audit log ID
- `user_id` - Acting user
- `action` - Action performed (login, delete, etc.)
- `resource_type` - What was affected (user, alert, etc.)
- `resource_id` - ID of resource
- `description` - Action details
- `ip_address` - Source IP
- `timestamp` - Action time

**Related Functions:**

```python
log_audit(user_id, action, resource_type, resource_id, description, ip_address)
```

---

### 11. **THREAT_INTELLIGENCE Table**

Stores external threat intelligence data.

```sql
CREATE TABLE threat_intelligence(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    threat_id TEXT UNIQUE,
    threat_type TEXT NOT NULL,
    source TEXT NOT NULL,
    description TEXT,
    affected_ips TEXT,
    affected_users TEXT,
    confidence_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
```

---

### 12. **SYSTEM_SETTINGS Table**

Configuration and system-wide settings.

```sql
CREATE TABLE system_settings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    data_type TEXT DEFAULT 'string',
    updated_by TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Related Functions:**

```python
get_setting(setting_key)
set_setting(setting_key, setting_value, updated_by)
```

---

### 13. **DETECTION_RULES Table**

Customizable rules for threat detection.

```sql
CREATE TABLE detection_rules(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT UNIQUE NOT NULL,
    rule_type TEXT NOT NULL,
    condition TEXT NOT NULL,
    severity TEXT DEFAULT 'medium',
    is_active BOOLEAN DEFAULT 1,
    description TEXT,
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

---

### 14. **DASHBOARD_STATS Table**

Daily aggregated statistics for dashboard.

```sql
CREATE TABLE dashboard_stats(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date DATE UNIQUE,
    total_logs INTEGER DEFAULT 0,
    total_alerts INTEGER DEFAULT 0,
    critical_alerts INTEGER DEFAULT 0,
    high_alerts INTEGER DEFAULT 0,
    medium_alerts INTEGER DEFAULT 0,
    low_alerts INTEGER DEFAULT 0,
    unique_ips INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    attack_attempts INTEGER DEFAULT 0,
    anomalies_detected INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

---

### 15. **SESSION_LOGS Table**

User session tracking for access logs.

```sql
CREATE TABLE session_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_time DATETIME,
    session_duration INTEGER,
    status TEXT DEFAULT 'active'
)
```

---

## Database Indexes

Indexes are created for frequently queried columns to improve performance:

```
idx_logs_ip                  - Fast IP lookups in logs
idx_logs_user                - Fast user lookups in logs
idx_logs_time                - Time-based log queries
idx_attack_history_ip        - Attack queries by IP
idx_attack_history_severity  - Filter attacks by severity
idx_anomaly_logs_ip          - Anomaly queries by IP
idx_alerts_severity          - Alert filtering
idx_alerts_created           - Recent alerts
idx_audit_logs_user          - User action audit trail
idx_ip_reputation_threat     - Threat level lookups
```

---

## Usage Examples

### Initialize Database

```python
from database import init_db

# Initialize all tables on first run
init_db()
```

### Insert Log Entries

```python
import pandas as pd
from database import insert_logs

# DataFrame with columns: time, status, user, ip
df = pd.DataFrame({
    'time': ['2024-01-15 10:30:00'],
    'status': ['FAILED'],
    'user': ['admin'],
    'ip': ['192.168.1.100']
})
insert_logs(df)
```

### Detect and Store Attack

```python
from database import insert_attack

alert = {
    'ip': '192.168.1.50',
    'type': 'brute_force',
    'attempts': 150,
    'severity': 'CRITICAL',
    'description': 'Multiple failed login attempts'
}
insert_attack(alert)
```

### Check IP Whitelist/Blacklist

```python
from database import is_ip_whitelisted, is_ip_blacklisted

if is_ip_blacklisted('192.168.1.50'):
    print("IP is blacklisted - block connection")

if is_ip_whitelisted('192.168.1.100'):
    print("IP is trusted - allow connection")
```

### Create User

```python
from database import create_user
from werkzeug.security import generate_password_hash

password_hash = generate_password_hash('password123')
create_user('john_analyst', password_hash, 'john@company.com', 'analyst')
```

### Get Database Statistics

```python
from database import get_db_stats

stats = get_db_stats()
print(f"Total logs: {stats['total_logs']}")
print(f"Active attacks: {stats['active_attacks']}")
print(f"Unread alerts: {stats['unread_alerts']}")
```

---

## Connection Management

The database uses a context manager for safe connection handling:

```python
from database import get_db_connection

# Automatic connection cleanup
with get_db_connection() as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM alerts WHERE severity = ?", ('CRITICAL',))
    results = c.fetchall()
```

---

## Data Retention & Cleanup

Automatically clean up old data:

```python
from database import clear_old_data

# Delete logs and emails older than 30 days
clear_old_data(days=30)
```

---

## Performance Tips

1. **Use Indexes**: Always filter by indexed columns (IP, user, severity, time)
2. **Limit Queries**: Use LIMIT when retrieving large datasets
3. **Batch Operations**: Insert multiple records at once with pandas
4. **Regular Cleanup**: Remove old data regularly to maintain performance
5. **Monitor Size**: Check database size periodically

```python
import os
db_size_mb = os.path.getsize('database/logs.db') / (1024 * 1024)
print(f"Database size: {db_size_mb:.2f} MB")
```

---

## Migration from Old System

If upgrading from the previous database structure:

```python
from database import init_db

# Old tables will be preserved
# New tables will be created automatically
init_db()

# Existing data remains intact
# Start using new functions for new data
```

---

## Backup and Restore

### Backup

```bash
cp database/logs.db database/logs_backup_$(date +%Y%m%d).db
```

### Restore

```bash
cp database/logs_backup_20240115.db database/logs.db
```

---

## Security Considerations

✅ **Implemented:**

- Password hashing for users (no plaintext storage)
- Audit logs for compliance
- User roles and permissions framework
- Session tracking
- Separate tables for sensitive data

⚠️ **Best Practices:**

- Always use parameterized queries (handled by functions)
- Enable database encryption for sensitive deployments
- Regularly backup database
- Monitor access logs
- Implement database-level permissions

---

## Database Diagram

```
┌─────────────────┐
│     USERS       │
└────────┬────────┘
         │
    ┌────┴─────────────────────────────┐
    │                                   │
┌───▼──────────────┐        ┌──────────▼────┐
│  SESSION_LOGS    │        │  AUDIT_LOGS   │
└──────────────────┘        └───────────────┘

┌──────────────┐
│    LOGS      │◄──────────────┐
└──────┬───────┘               │
       │                       │
  ┌────┴─────────────────────┐ │
  │                          │ │
  ▼                          ▼ │
┌─────────────┐      ┌──────────────┐
│ ATTACK_     │      │   ANOMALY_   │
│ HISTORY     │      │   LOGS       │
└────┬────────┘      └──────────────┘
     │
     │         ┌───────────────────┐
     ├────────▶│     ALERTS        │
     │         └────┬──────────────┘
     │              │
     │              └────┐
     │                   ▼
     │         ┌──────────────────────┐
     └────────▶│  EMAIL_              │
               │  NOTIFICATIONS       │
               └──────────────────────┘

┌──────────────────┐
│   IP_REPUTATION  │
└────┬─────────────┘
     │
     ├──────┬──────────┐
     │      │          │
     ▼      ▼          ▼
  WHITELIST BLACKLIST THREAT_
                      INTELLIGENCE

┌─────────────────┐   ┌──────────────┐
│ DETECTION_      │   │ DASHBOARD_   │
│ RULES           │   │ STATS        │
└─────────────────┘   └──────────────┘

┌────────────────────┐
│  SYSTEM_SETTINGS   │
└────────────────────┘
```

---

## Support & Troubleshooting

### Issue: Database locked

**Solution:** Close all open connections and restart application

### Issue: Slow queries

**Solution:** Check if proper indexes exist and data isn't too old

### Issue: Disk space

**Solution:** Run `clear_old_data()` to remove old records

For more help, check application logs in `logs/` directory.
