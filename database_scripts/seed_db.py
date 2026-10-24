import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hosteliq.db")
SEED_PATH = os.path.join(os.path.dirname(__file__), "seed_data.sql")

def seed_database():
    if not os.path.exists(SEED_PATH):
        print("Seed file not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print("Seed data populated successfully.")

if __name__ == "__main__":
    seed_database()
