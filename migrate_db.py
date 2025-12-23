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


def table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def add_column_if_missing(cursor, table_name, column_name, column_type, default=None):
    """Add a column to table if it doesn't exist"""
    existing = get_existing_columns(cursor, table_name)

    if column_name in existing:
        print(f"  ✓ Column '{column_name}' already exists")
        return False

    # Build the ALTER TABLE statement
    sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    if default is not None:
        sql += f" DEFAULT {default}"

    cursor.execute(sql)
    print(f"  + Added column '{column_name}'")
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

        if not table_exists(cursor, 'drivers'):
            print("  ERROR: 'drivers' table does not exist!")
        else:
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
        # MISSIONS TABLE MIGRATIONS
        # ============================================
        print("\n[Migrating 'missions' table...]")

        if not table_exists(cursor, 'missions'):
            print("  ERROR: 'missions' table does not exist!")
        else:
            # Mission type and source
            add_column_if_missing(cursor, 'missions', 'mission_type', "VARCHAR(20)", "'admin_assigned'")
            add_column_if_missing(cursor, 'missions', 'app_name', 'VARCHAR(50)', 'NULL')
            add_column_if_missing(cursor, 'missions', 'expected_cost', 'FLOAT', 'NULL')

            # Route details
            add_column_if_missing(cursor, 'missions', 'from_location', 'VARCHAR(200)', "''")
            add_column_if_missing(cursor, 'missions', 'to_location', 'VARCHAR(200)', "''")
            add_column_if_missing(cursor, 'missions', 'distance_km', 'FLOAT', '0')

            # Timing
            add_column_if_missing(cursor, 'missions', 'mission_date', 'DATE', 'NULL')
            add_column_if_missing(cursor, 'missions', 'start_time', 'TIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'end_time', 'TIME', 'NULL')

            # Financial details
            add_column_if_missing(cursor, 'missions', 'total_revenue', 'FLOAT', '0')
            add_column_if_missing(cursor, 'missions', 'fuel_cost', 'FLOAT', '0')
            add_column_if_missing(cursor, 'missions', 'driver_fees', 'FLOAT', '0')
            add_column_if_missing(cursor, 'missions', 'company_profit', 'FLOAT', '0')

            # Status and workflow
            add_column_if_missing(cursor, 'missions', 'status', "VARCHAR(20)", "'pending'")
            add_column_if_missing(cursor, 'missions', 'notes', 'TEXT', 'NULL')

            # Approval workflow
            add_column_if_missing(cursor, 'missions', 'is_approved', 'BOOLEAN', '0')
            add_column_if_missing(cursor, 'missions', 'approved_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'can_start', 'BOOLEAN', '0')

            # Timestamps
            add_column_if_missing(cursor, 'missions', 'created_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'started_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'ended_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'completed_at', 'DATETIME', 'NULL')

        # ============================================
        # FLEET_CARS TABLE MIGRATIONS (if needed)
        # ============================================
        print("\n[Checking 'fleet_cars' table...]")

        if not table_exists(cursor, 'fleet_cars'):
            print("  ERROR: 'fleet_cars' table does not exist!")
        else:
            # Add any fleet_cars columns if needed in the future
            print("  ✓ Table exists, no migrations needed")

        # ============================================
        # COMMIT CHANGES
        # ============================================
        conn.commit()
        print("\n" + "=" * 50)
        print("✓ All migrations completed successfully!")
        print("=" * 50)
        return True

    except Exception as e:
        conn.rollback()
        print(f"\nERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 50)
    print("IPI Database Migration Script")
    print("=" * 50)
    migrate()
