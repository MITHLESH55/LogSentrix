#!/usr/bin/env python
"""Database Audit Script"""

import sqlite3
import os

DB_PATH = "database/logs.db"

print("=" * 70)
print("  DATABASE AUDIT REPORT - LogSentrix")
print("=" * 70)

# Check if database file exists
if not os.path.exists(DB_PATH):
    print(f"\n✗ ERROR: Database file not found at {DB_PATH}")
    exit(1)

print(f"\n✓ Database file found: {DB_PATH}")
print(f"  Size: {os.path.getsize(DB_PATH)} bytes")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check for users table
print("\n" + "=" * 70)
print("1. CHECKING USERS TABLE")
print("=" * 70)

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
users_table = c.fetchone()

if users_table:
    print("✓ Users table EXISTS")
    
    # Get table schema
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
    schema = c.fetchone()[0]
    print("\nTable Schema:")
    print(schema)
    
    # Get all users
    c.execute("SELECT id, username, email, role, created_at FROM users")
    users = c.fetchall()
    print(f"\nTotal users in database: {len(users)}")
    
    if users:
        print("\nAll users in database:")
        print("-" * 70)
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}, Created: {user[4]}")
        
        # Check for specific user
        print("\n" + "=" * 70)
        print("2. SEARCHING FOR SPECIFIC USER")
        print("=" * 70)
        c.execute("SELECT * FROM users WHERE username LIKE '%mithlesh%'")
        specific_user = c.fetchone()
        if specific_user:
            print("✓ User with 'mithlesh' found in database:")
            print(f"  {specific_user}")
        else:
            print("✗ No user with 'mithlesh' found in database")
    else:
        print("✗ No users found in database!")
else:
    print("✗ Users table DOES NOT EXIST")

# Check other tables
print("\n" + "=" * 70)
print("3. OTHER TABLES IN DATABASE")
print("=" * 70)

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print(f"Total tables: {len(tables)}")
for table in tables:
    c.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = c.fetchone()[0]
    print(f"  - {table[0]}: {count} records")

# Check if password_hash column exists
print("\n" + "=" * 70)
print("4. CHECKING USERS TABLE COLUMNS")
print("=" * 70)

c.execute("PRAGMA table_info(users)")
columns = c.fetchall()
if columns:
    print("Users table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check what columns we have
    col_names = [col[1] for col in columns]
    required_cols = ['username', 'password_hash', 'email']
    print("\nRequired fields check:")
    for req_col in required_cols:
        status = "✓" if req_col in col_names else "✗"
        print(f"  {status} {req_col}")

conn.close()

print("\n" + "=" * 70)
print("  END OF AUDIT")
print("=" * 70)
