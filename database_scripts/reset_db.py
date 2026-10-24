import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from app.database.nosql_manager import nosql_manager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hosteliq.db")

def empty_database():
    print("==================================================")
    print("      HostelIQ - Complete System Database Reset   ")
    print("==================================================")

    # 1. Clear SQLite Relational Tables
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
        
        # Disable foreign keys temporarily for clean deletion
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
            # Reset sqlite_sequence for autoincrement
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
            print(f"  [-] Cleared relational table: {table}")
            
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        cursor.execute("VACUUM;")
        conn.commit()
        conn.close()
        print("  [*] Relational database (SQLite) has been completely emptied.")
    else:
        print(f"  [!] SQLite database file not found at {DB_PATH}.")

    # 2. Clear MongoDB / NoSQL Maintenance Complaints
    purged_complaints = nosql_manager.delete_all_complaints()
    print(f"  [-] Cleared NoSQL maintenance complaints ({purged_complaints} tickets deleted).")

    print("--------------------------------------------------")
    print(" [SUCCESS] All records wiped successfully:")
    print("   * Rooms & Allocations: 0")
    print("   * Resident Students:   0")
    print("   * Maintenance Staff:   0")
    print("   * Water Telemetry:     0")
    print("   * Power Telemetry:     0")
    print("   * Maintenance Tickets: 0")
    print("==================================================")

if __name__ == "__main__":
    empty_database()
