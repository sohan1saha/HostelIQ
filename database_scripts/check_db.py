import sqlite3

conn = sqlite3.connect("hosteliq.db")
cursor = conn.cursor()
tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
print("Current table row counts:")
for t in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  - {t}: {count} rows")
conn.close()
