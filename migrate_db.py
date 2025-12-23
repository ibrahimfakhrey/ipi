#!/usr/bin/env python3
"""
Database Migration Script for PythonAnywhere
Run this script to add missing columns to the database.

Usage: python migrate_db.py
"""

import sqlite3
import os

# Path to your database - adjust if needed
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'ipi.db')

# If database is in a different location on PythonAnywhere, uncomment and modify:
# DB_PATH = '/home/amsfiles/ipi/instance/ipi.db'


def get_existing_columns(cursor, table_name):
    """Get list of existing columns in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def add_column_if_missing(cursor, table_name, column_name, column_type, default=None):
    """Add a column to table if it doesn't exist"""
    existing = get_existing_columns(cursor, table_name)

    if column_name in existing:
        print(f"  ✓ Column '{column_name}' already exists in '{table_name}'")
        return False

    # Build the ALTER TABLE statement
    sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    if default is not None:
        sql += f" DEFAULT {default}"

    cursor.execute(sql)
    print(f"  ✓ Added column '{column_name}' to '{table_name}'")
    return True


def migrate():
    """Run all migrations"""
    print(f"Connecting to database: {DB_PATH}")

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Please update DB_PATH in this script to point to your database.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # ============================================
        # DRIVERS TABLE MIGRATIONS
        # ============================================
        print("\n[Migrating 'drivers' table...]")

        # Check if drivers table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='drivers'")
        if not cursor.fetchone():
            print("  ERROR: 'drivers' table does not exist!")
            return False

        # Add new columns for driver mobile app
        add_column_if_missing(cursor, 'drivers', 'driver_number', 'VARCHAR(20)', 'NULL')
        add_column_if_missing(cursor, 'drivers', 'password_hash', 'VARCHAR(256)', 'NULL')
        add_column_if_missing(cursor, 'drivers', 'fcm_token', 'VARCHAR(500)', 'NULL')
        add_column_if_missing(cursor, 'drivers', 'is_verified', 'BOOLEAN', '0')
        add_column_if_missing(cursor, 'drivers', 'photo_filename', 'VARCHAR(300)', 'NULL')
        add_column_if_missing(cursor, 'drivers', 'license_filename', 'VARCHAR(300)', 'NULL')
        add_column_if_missing(cursor, 'drivers', 'rating', 'FLOAT', '0.0')
        add_column_if_missing(cursor, 'drivers', 'completed_missions', 'INTEGER', '0')
        add_column_if_missing(cursor, 'drivers', 'is_approved', 'BOOLEAN', '0')

        # ============================================
        # COMMIT CHANGES
        # ============================================
        conn.commit()
        print("\n✓ All migrations completed successfully!")
        return True

    except Exception as e:
        conn.rollback()
        print(f"\nERROR during migration: {e}")
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 50)
    print("IPI Database Migration Script")
    print("=" * 50)
    migrate()
