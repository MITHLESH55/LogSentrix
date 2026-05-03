"""
Database Verification and Testing Script
Tests all SQLite database tables and functions
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from database import *
from werkzeug.security import generate_password_hash
import pandas as pd

def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_initialization():
    """Test database initialization."""
    print_section("TEST 1: Database Initialization")
    
    try:
        print("[OK] Initializing database...")
        init_db()
        print("[OK] All tables created successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_user_management():
    """Test user creation and retrieval."""
    print_section("TEST 2: User Management")
    
    try:
        # Create user
        print("[OK] Creating test user...")
        password_hash = generate_password_hash('TestPassword123')
        created = create_user(
            'testuser',
            password_hash,
            'testuser@company.com',
            'analyst'
        )
        assert created, "Failed to create user"
        
        # Retrieve user
        print("[OK] Retrieving user...")
        user = get_user('testuser')
        assert user is not None, "User not found"
        assert user['username'] == 'testuser', "Username mismatch"
        assert user['role'] == 'analyst', "Role mismatch"
        
        # Update login
        print("[OK] Updating last login...")
        update_last_login('testuser')
        
        print("[OK] User management tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_logs():
    """Test log insertion and retrieval."""
    print_section("TEST 3: Log Management")
    
    try:
        # Create sample logs
        print("[OK] Creating sample logs...")
        df = pd.DataFrame({
            'time': [
                '2024-01-15 10:30:00',
                '2024-01-15 10:31:00',
                '2024-01-15 10:32:00'
            ],
            'status': ['SUCCESS', 'FAILED', 'SUCCESS'],
            'user': ['admin', 'hacker', 'user1'],
            'ip': ['192.168.1.100', '10.0.0.50', '192.168.1.101']
        })
        
        insert_logs(df)
        
        # Retrieve logs
        print("[OK] Retrieving recent logs...")
        logs = get_recent_logs(limit=10)
        assert len(logs) > 0, "No logs found"
        
        print(f"[OK] Stored and retrieved {len(logs)} logs")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_attack_detection():
    """Test attack history storage."""
    print_section("TEST 4: Attack Detection")
    
    try:
        # Insert attack
        print("[OK] Inserting attack record...")
        alert = {
            'ip': '10.0.0.50',
            'type': 'brute_force',
            'attempts': 150,
            'severity': 'CRITICAL',
            'description': 'Multiple failed login attempts detected'
        }
        insert_attack(alert)
        
        # Retrieve active attacks
        print("[OK] Retrieving active attacks...")
        attacks = get_active_attacks()
        assert len(attacks) > 0, "No attacks found"
        assert attacks[0]['ip'] == '10.0.0.50', "IP mismatch"
        
        # Resolve attack
        print("[OK] Resolving attack...")
        resolve_attack(attacks[0]['id'], 'testuser')
        
        print("[OK] Attack detection tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_anomaly_detection():
    """Test anomaly logging."""
    print_section("TEST 5: Anomaly Detection")
    
    try:
        # Insert anomaly
        print("[OK] Inserting anomaly record...")
        insert_anomaly(
            ip='192.168.1.50',
            user='suspicious_user',
            reason='ML model detected unusual login pattern',
            anomaly_score=87.5
        )
        
        # Retrieve anomalies
        print("[OK] Retrieving active anomalies...")
        anomalies = get_active_anomalies()
        assert len(anomalies) > 0, "No anomalies found"
        
        print("[OK] Anomaly detection tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_ip_management():
    """Test IP whitelist and blacklist."""
    print_section("TEST 6: IP Management")
    
    try:
        # Test whitelist
        print("[OK] Adding IP to whitelist...")
        added = add_ip_whitelist(
            '192.168.1.200',
            'Company VPN',
            'admin',
            'Internal network'
        )
        assert added, "Failed to add to whitelist"
        
        is_white = is_ip_whitelisted('192.168.1.200')
        assert is_white, "IP not found in whitelist"
        print("[OK] IP whitelist works")
        
        # Test blacklist
        print("[OK] Adding IP to blacklist...")
        added = add_ip_blacklist(
            '10.0.0.50',
            'Known botnet',
            'critical',
            'admin',
            block_duration=1440
        )
        assert added, "Failed to add to blacklist"
        
        is_black = is_ip_blacklisted('10.0.0.50')
        assert is_black, "IP not found in blacklist"
        print("[OK] IP blacklist works")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_ip_reputation():
    """Test IP reputation storage."""
    print_section("TEST 7: IP Reputation")
    
    try:
        # Insert reputation
        print("[OK] Storing IP reputation...")
        insert_ip_reputation(
            ip='10.0.0.60',
            reputation='malicious',
            threat_level='critical',
            source='AbuseIPDB'
        )
        
        # Retrieve reputation
        print("[OK] Retrieving IP reputation...")
        rep = get_ip_reputation('10.0.0.60')
        assert rep is not None, "Reputation not found"
        assert rep['threat_level'] == 'critical', "Threat level mismatch"
        
        print("[OK] IP reputation tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_alerts():
    """Test alert creation and management."""
    print_section("TEST 8: Alert Management")
    
    try:
        # Create alert
        print("[OK] Creating alert...")
        alert_id = insert_alert(
            alert_type='brute_force',
            severity='CRITICAL',
            ip='10.0.0.50',
            user='attacker',
            title='Brute Force Attack Detected',
            description='150+ failed login attempts from 10.0.0.50'
        )
        assert alert_id is not None, "Failed to create alert"
        
        # Get unread alerts
        print("[OK] Retrieving unread alerts...")
        unread = get_unread_alerts()
        assert len(unread) > 0, "No unread alerts"
        
        # Mark as read
        print("[OK] Marking alert as read...")
        mark_alert_read(alert_id)
        
        print("[OK] Alert management tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_email_notifications():
    """Test email notification logging."""
    print_section("TEST 9: Email Notifications")
    
    try:
        # Insert notification
        print("[OK] Creating email notification record...")
        email_id = insert_email_notification(
            recipient_email='admin@company.com',
            subject='CRITICAL: Brute Force Attack Detected',
            message='Multiple failed login attempts detected from 10.0.0.50',
            alert_id=None
        )
        assert email_id is not None, "Failed to create notification"
        
        # Mark as sent
        print("[OK] Marking email as sent...")
        mark_email_sent(email_id)
        
        print("[OK] Email notification tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_audit_logging():
    """Test audit trail logging."""
    print_section("TEST 10: Audit Logging")
    
    try:
        # Log action
        print("[OK] Logging user action...")
        log_audit(
            user_id='testuser',
            action='acknowledge_alert',
            resource_type='alert',
            resource_id=1,
            description='Acknowledged critical alert',
            ip_address='192.168.1.100'
        )
        
        print("[OK] Audit logging works")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_system_settings():
    """Test system settings storage."""
    print_section("TEST 11: System Settings")
    
    try:
        # Set setting
        print("[OK] Setting configuration value...")
        set_setting('alert_threshold', '10', 'admin')
        
        # Get setting
        print("[OK] Retrieving configuration value...")
        value = get_setting('alert_threshold')
        assert value == '10', "Setting value mismatch"
        
        print("[OK] System settings tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_session_logging():
    """Test session tracking."""
    print_section("TEST 12: Session Logging")
    
    try:
        # Log session
        print("[OK] Creating session log...")
        session_id = log_session(
            'testuser',
            '192.168.1.100',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        assert session_id is not None, "Failed to log session"
        
        # End session
        print("[OK] Ending session...")
        end_session(session_id)
        
        print("[OK] Session logging tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_database_stats():
    """Test database statistics."""
    print_section("TEST 13: Database Statistics")
    
    try:
        print("[OK] Retrieving database statistics...")
        stats = get_db_stats()
        
        assert 'total_logs' in stats, "Missing total_logs"
        assert 'active_attacks' in stats, "Missing active_attacks"
        assert 'active_anomalies' in stats, "Missing active_anomalies"
        assert 'unread_alerts' in stats, "Missing unread_alerts"
        
        print(f"  Total logs: {stats['total_logs']}")
        print(f"  Active attacks: {stats['active_attacks']}")
        print(f"  Active anomalies: {stats['active_anomalies']}")
        print(f"  Unread alerts: {stats['unread_alerts']}")
        print(f"  Unique IPs: {stats['unique_ips']}")
        print(f"  Unique users: {stats['unique_users']}")
        
        print("[OK] Database statistics tests passed")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  SQLite Database Verification Script")
    print("  LogSentrix Security Monitoring System")
    print("="*60)
    
    tests = [
        test_initialization,
        test_user_management,
        test_logs,
        test_attack_detection,
        test_anomaly_detection,
        test_ip_management,
        test_ip_reputation,
        test_alerts,
        test_email_notifications,
        test_audit_logging,
        test_system_settings,
        test_session_logging,
        test_database_stats,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Unexpected error: {e}")
            results.append(False)
    
    # Summary
    print_section("Test Summary")
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[OK] All tests passed! Database is ready to use.\n")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Check errors above.\n")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
