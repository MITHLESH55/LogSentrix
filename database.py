import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "database/logs.db"

# ================================================================
# DATABASE INITIALIZATION & CONNECTION
# ================================================================

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize all database tables."""
    os.makedirs("database", exist_ok=True)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # --------------------------
        # USERS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
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
        """)
        
        # --------------------------
        # LOGS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            user TEXT NOT NULL,
            ip TEXT NOT NULL,
            source_file TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # --------------------------
        # ATTACK HISTORY TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS attack_history(
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
        """)
        
        # --------------------------
        # ANOMALY LOGS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS anomaly_logs(
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
        """)
        
        # --------------------------
        # IP REPUTATION TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS ip_reputation(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT UNIQUE NOT NULL,
            reputation TEXT NOT NULL,
            threat_level TEXT,
            abuse_reports INTEGER DEFAULT 0,
            blacklist_count INTEGER DEFAULT 0,
            last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT
        )
        """)
        
        # --------------------------
        # IP WHITELIST TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS ip_whitelist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT UNIQUE NOT NULL,
            description TEXT,
            added_by TEXT,
            reason TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME
        )
        """)
        
        # --------------------------
        # IP BLACKLIST TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS ip_blacklist(
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
        """)
        
        # --------------------------
        # ALERTS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS alerts(
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
        """)
        
        # --------------------------
        # EMAIL NOTIFICATIONS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS email_notifications(
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
        """)
        
        # --------------------------
        # AUDIT LOGS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id INTEGER,
            description TEXT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # --------------------------
        # THREAT INTELLIGENCE TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS threat_intelligence(
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
        """)
        
        # --------------------------
        # SYSTEM SETTINGS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS system_settings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            data_type TEXT DEFAULT 'string',
            updated_by TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # --------------------------
        # DETECTION RULES TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS detection_rules(
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
        """)
        
        # --------------------------
        # DASHBOARD STATISTICS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_stats(
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
        """)
        
        # --------------------------
        # SESSION LOGS TABLE
        # --------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS session_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            logout_time DATETIME,
            session_duration INTEGER,
            status TEXT DEFAULT 'active'
        )
        """)
        
        # Create indexes for better query performance
        c.execute("CREATE INDEX IF NOT EXISTS idx_logs_ip ON logs(ip)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_logs_time ON logs(time)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_attack_history_ip ON attack_history(ip)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_attack_history_severity ON attack_history(severity)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_anomaly_logs_ip ON anomaly_logs(ip)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_ip_reputation_threat ON ip_reputation(threat_level)")
        
        conn.commit()


# ================================================================
# USER MANAGEMENT FUNCTIONS
# ================================================================

def create_user(username, password_hash, email=None, role='analyst'):
    """Create a new user."""
    print(f"[DB] Attempting to create user: {username}")
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO users(username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
            """, (username, password_hash, email, role))
            conn.commit()
            print(f"[DB] Successfully created user: {username}")
            return True
    except sqlite3.IntegrityError:
        print(f"[DB] Error: User '{username}' already exists.")
        return False
    except Exception as e:
        print(f"[DB ERROR] Creating user '{username}': {e}")
        return False


def get_user(username):
    """Get user by username."""
    print(f"[DB] Querying user: {username}")
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            if user:
                print(f"[DB] User found: {username}")
            else:
                print(f"[DB] User NOT found: {username}")
            return user
    except Exception as e:
        print(f"[DB ERROR] Getting user '{username}': {e}")
        return None


def update_last_login(username):
    """Update user's last login time."""
    print(f"[DB] Updating last login for: {username}")
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE username = ?
            """, (username,))
            conn.commit()
            print(f"[DB] Updated last login for: {username}")
    except Exception as e:
        print(f"[DB ERROR] Updating last login for '{username}': {e}")


# ================================================================
# LOGS FUNCTIONS
# ================================================================

def insert_logs(df):
    """Insert log entries from dataframe."""
    if df is None or len(df) == 0:
        return
    
    with get_db_connection() as conn:
        try:
            df.drop_duplicates(inplace=True)
            df[["time", "status", "user", "ip"]].to_sql(
                "logs",
                conn,
                if_exists="append",
                index=False
            )
        except Exception as e:
            print(f"[DB ERROR] Inserting logs: {e}")


def get_recent_logs(limit=100):
    """Get recent log entries."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM logs 
            ORDER BY created_at DESC 
            LIMIT ?
            """, (limit,))
            return c.fetchall()
    except Exception as e:
        print(f"[DB ERROR] Getting logs: {e}")
        return []


# ================================================================
# ATTACK HISTORY FUNCTIONS
# ================================================================

def insert_attack(alert):
    """Store detected attack."""
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("""
            INSERT INTO attack_history(ip, attack_type, attempts, severity, description)
            VALUES (?, ?, ?, ?, ?)
            """, (
                alert.get("ip"),
                alert.get("type"),
                alert.get("attempts"),
                alert.get("severity"),
                alert.get("description", "")
            ))
            conn.commit()
        except Exception as e:
            print(f"[DB ERROR] Inserting attack: {e}")


def get_active_attacks():
    """Get all active (unresolved) attacks."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM attack_history 
            WHERE status = 'open' 
            ORDER BY timestamp DESC
            """)
            return c.fetchall()
    except Exception as e:
        print(f"[DB ERROR] Getting attacks: {e}")
        return []


def resolve_attack(attack_id, resolved_by):
    """Mark attack as resolved."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            UPDATE attack_history 
            SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP, resolved_by = ?
            WHERE id = ?
            """, (resolved_by, attack_id))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Resolving attack: {e}")


# ================================================================
# ANOMALY FUNCTIONS
# ================================================================

def insert_anomaly(ip, user, reason, anomaly_score=None):
    """Store detected anomaly."""
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("""
            INSERT INTO anomaly_logs(ip, user, reason, anomaly_score)
            VALUES (?, ?, ?, ?)
            """, (ip, user, reason, anomaly_score))
            conn.commit()
        except Exception as e:
            print(f"[DB ERROR] Inserting anomaly: {e}")


def get_active_anomalies():
    """Get all active (unresolved) anomalies."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM anomaly_logs 
            WHERE status = 'open' 
            ORDER BY timestamp DESC
            """)
            return c.fetchall()
    except Exception as e:
        print(f"[DB ERROR] Getting anomalies: {e}")
        return []


# ================================================================
# IP REPUTATION FUNCTIONS
# ================================================================

def insert_ip_reputation(ip, reputation, threat_level=None, source=None):
    """Store IP reputation results."""
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("""
            INSERT OR REPLACE INTO ip_reputation(ip, reputation, threat_level, source, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (ip, reputation, threat_level, source))
            conn.commit()
        except Exception as e:
            print(f"[DB ERROR] Inserting IP reputation: {e}")


def get_ip_reputation(ip):
    """Get IP reputation information."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM ip_reputation WHERE ip = ?", (ip,))
            return c.fetchone()
    except Exception as e:
        print(f"[DB ERROR] Getting IP reputation: {e}")
        return None


# ================================================================
# IP WHITELIST FUNCTIONS
# ================================================================

def add_ip_whitelist(ip, description, added_by, reason):
    """Add IP to whitelist."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO ip_whitelist(ip, description, added_by, reason)
            VALUES (?, ?, ?, ?)
            """, (ip, description, added_by, reason))
            conn.commit()
            return True
    except Exception as e:
        print(f"[DB ERROR] Adding to whitelist: {e}")
        return False


def is_ip_whitelisted(ip):
    """Check if IP is whitelisted."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT id FROM ip_whitelist 
            WHERE ip = ? AND is_active = 1
            """, (ip,))
            return c.fetchone() is not None
    except Exception as e:
        print(f"[DB ERROR] Checking whitelist: {e}")
        return False


# ================================================================
# IP BLACKLIST FUNCTIONS
# ================================================================

def add_ip_blacklist(ip, reason, severity, added_by, block_duration=None):
    """Add IP to blacklist."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO ip_blacklist(ip, reason, severity, added_by, block_duration)
            VALUES (?, ?, ?, ?, ?)
            """, (ip, reason, severity, added_by, block_duration))
            conn.commit()
            return True
    except Exception as e:
        print(f"[DB ERROR] Adding to blacklist: {e}")
        return False


def is_ip_blacklisted(ip):
    """Check if IP is blacklisted."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT id FROM ip_blacklist 
            WHERE ip = ? AND is_active = 1
            """, (ip,))
            return c.fetchone() is not None
    except Exception as e:
        print(f"[DB ERROR] Checking blacklist: {e}")
        return False


# ================================================================
# ALERTS FUNCTIONS
# ================================================================

def insert_alert(alert_type, severity, ip, user, title, description):
    """Create new alert."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO alerts(alert_type, severity, ip, user, title, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (alert_type, severity, ip, user, title, description))
            conn.commit()
            return c.lastrowid
    except Exception as e:
        print(f"[DB ERROR] Inserting alert: {e}")
        return None


def get_unread_alerts():
    """Get unread alerts."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM alerts 
            WHERE is_read = 0 
            ORDER BY created_at DESC
            """)
            return c.fetchall()
    except Exception as e:
        print(f"[DB ERROR] Getting unread alerts: {e}")
        return []


def mark_alert_read(alert_id):
    """Mark alert as read."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            UPDATE alerts 
            SET is_read = 1 
            WHERE id = ?
            """, (alert_id,))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Marking alert read: {e}")


# ================================================================
# EMAIL NOTIFICATION FUNCTIONS
# ================================================================

def insert_email_notification(recipient_email, subject, message, alert_id=None):
    """Log email notification."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO email_notifications(recipient_email, subject, message, alert_id)
            VALUES (?, ?, ?, ?)
            """, (recipient_email, subject, message, alert_id))
            conn.commit()
            return c.lastrowid
    except Exception as e:
        print(f"[DB ERROR] Inserting email notification: {e}")
        return None


def mark_email_sent(email_id):
    """Mark email as sent."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            UPDATE email_notifications 
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """, (email_id,))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Marking email sent: {e}")


# ================================================================
# AUDIT LOG FUNCTIONS
# ================================================================

def log_audit(user_id, action, resource_type=None, resource_id=None, description=None, ip_address=None):
    """Log user action for audit trail."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO audit_logs(user_id, action, resource_type, resource_id, description, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, action, resource_type, resource_id, description, ip_address))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Logging audit: {e}")


# ================================================================
# SYSTEM SETTINGS FUNCTIONS
# ================================================================

def get_setting(setting_key):
    """Get system setting."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT setting_value FROM system_settings 
            WHERE setting_key = ?
            """, (setting_key,))
            result = c.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"[DB ERROR] Getting setting: {e}")
        return None


def set_setting(setting_key, setting_value, updated_by=None):
    """Set system setting."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT OR REPLACE INTO system_settings(setting_key, setting_value, updated_by)
            VALUES (?, ?, ?)
            """, (setting_key, setting_value, updated_by))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Setting setting: {e}")


# ================================================================
# DASHBOARD STATS FUNCTIONS
# ================================================================

def get_daily_stats(date_str=None):
    """Get daily statistics."""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM dashboard_stats 
            WHERE stat_date = ?
            """, (date_str,))
            return c.fetchone()
    except Exception as e:
        print(f"[DB ERROR] Getting daily stats: {e}")
        return None


def update_daily_stats(stat_date, **kwargs):
    """Update daily statistics."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [stat_date]
            c.execute(f"""
            INSERT OR REPLACE INTO dashboard_stats(stat_date, {', '.join(kwargs.keys())})
            VALUES (?, {', '.join(['?' for _ in kwargs])})
            """, [stat_date] + list(kwargs.values()))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Updating daily stats: {e}")


# ================================================================
# SESSION LOG FUNCTIONS
# ================================================================

def log_session(user_id, ip_address, user_agent):
    """Create session log entry."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO session_logs(user_id, ip_address, user_agent)
            VALUES (?, ?, ?)
            """, (user_id, ip_address, user_agent))
            conn.commit()
            return c.lastrowid
    except Exception as e:
        print(f"[DB ERROR] Logging session: {e}")
        return None


def end_session(session_id):
    """End session log entry."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            UPDATE session_logs 
            SET logout_time = CURRENT_TIMESTAMP, status = 'closed'
            WHERE id = ?
            """, (session_id,))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Ending session: {e}")


# ================================================================
# DATABASE UTILITY FUNCTIONS
# ================================================================

def get_db_stats():
    """Get database statistics."""
    stats = {}
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            c.execute("SELECT COUNT(*) FROM logs")
            stats['total_logs'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM attack_history WHERE status = 'open'")
            stats['active_attacks'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM anomaly_logs WHERE status = 'open'")
            stats['active_anomalies'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
            stats['unread_alerts'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT ip) FROM logs")
            stats['unique_ips'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT user) FROM logs")
            stats['unique_users'] = c.fetchone()[0]
            
    except Exception as e:
        print(f"[DB ERROR] Getting stats: {e}")
    
    return stats


def clear_old_data(days=30):
    """Clear data older than specified days."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            c.execute("""
            DELETE FROM logs 
            WHERE created_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            c.execute("""
            DELETE FROM email_notifications 
            WHERE status = 'sent' 
            AND created_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            conn.commit()
            print(f"[DB] Cleaned up data older than {days} days")
    except Exception as e:
        print(f"[DB ERROR] Clearing old data: {e}")


if __name__ == "__main__":
    print("[INFO] Initializing database...")
    init_db()
    print("[INFO] Database initialized successfully!")
    stats = get_db_stats()
    print(f"[INFO] Database stats: {stats}")