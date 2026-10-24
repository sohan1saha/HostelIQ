#!/usr/bin/env python3
"""
HostelIQ - Comprehensive Database Generator
Creates:
- 10 Hostel Blocks: Block-A to Block-J
- 6 Floors per Block (Floors 1 to 6)
- 10 Rooms per Floor (Rooms 01 to 10, e.g., A-101 to A-110 ... A-601 to A-610)
- Total: 600 Rooms
- Capacity: 3 Occupants per Room (Total 1,800 Beds)
- 100% Full Occupancy: 1,800 Registered Students (3 students per room)
- Maintenance Staff (Plumbing, Electrical, Sanitation)
- Initial Smart Meter IoT Telemetry for all 600 rooms
"""

import sqlite3
import os
import random
from datetime import date
from faker import Faker

fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hosteliq.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

BLOCK_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
FLOORS_PER_BLOCK = 6
ROOMS_PER_FLOOR = 10
CAPACITY_PER_ROOM = 3

def populate_database(target_student_count: int = 1800):
    print("================================================================")
    print("      HostelIQ: Enterprise Multi-Block Database Generator       ")
    print("================================================================")

    # Validate bounds
    target_student_count = max(0, min(1800, target_student_count))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Initialize Schema
    print("[1/4] Ensuring fresh database schema...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()

    # Clear old records
    cursor.execute("PRAGMA foreign_keys = OFF;")
    for tbl in ["water_consumption", "electricity_consumption", "students", "maintenance_staff", "rooms"]:
        cursor.execute(f"DELETE FROM {tbl};")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tbl}';")
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    # 2. Generate 600 Rooms
    print("[2/4] Provisioning 600 Rooms across 10 Blocks & 6 Floors...")
    rooms_data = []
    room_id = 1
    for letter in BLOCK_LETTERS:
        block_name = f"Block-{letter}"
        for fl in range(1, FLOORS_PER_BLOCK + 1):
            for r_idx in range(1, ROOMS_PER_FLOOR + 1):
                room_no = f"{letter}-{fl}{r_idx:02d}"  # e.g., A-101, A-110, A-601
                rooms_data.append((room_id, block_name, fl, room_no, CAPACITY_PER_ROOM))
                room_id += 1

    cursor.executemany(
        "INSERT INTO rooms (room_id, block, floor, room_number, capacity) VALUES (?, ?, ?, ?, ?)",
        rooms_data
    )
    conn.commit()
    print(f"  -> Generated {len(rooms_data)} rooms (10 blocks x 6 floors x 10 rooms, 3 beds each = 1,800 beds).")

    # 3. Generate Students up to target_student_count
    print(f"[3/4] Registering {target_student_count} Students across rooms...")
    students_data = []
    stu_counter = 1

    for r_id, b_name, fl, r_no, cap in rooms_data:
        if stu_counter > target_student_count:
            break
        for bed in range(1, CAPACITY_PER_ROOM + 1):
            if stu_counter > target_student_count:
                break
            stu_id = f"STU2025{stu_counter:04d}"
            name = fake.name()
            clean_name = "".join(c for c in name.lower() if c.isalnum() or c == ' ').strip().replace(' ', '.')
            email = f"{clean_name}{stu_counter}@sitpune.edu.in"
            students_data.append((stu_id, name, email, r_id))
            stu_counter += 1

    if students_data:
        cursor.executemany(
            "INSERT INTO students (student_id, name, email, room_id) VALUES (?, ?, ?, ?)",
            students_data
        )
        conn.commit()
    print(f"  -> Registered {len(students_data)} students with room assignments.")

    # 4. Generate Maintenance Staff
    print("[4/4] Adding Maintenance Staff roster...")
    staff_data = [
        (101, 'Rajesh Kumar', 'Plumbing (SDG 6)', '+919876543210'),
        (102, 'Suresh Yadav', 'Electrical (SDG 12)', '+919876543211'),
        (103, 'Amit Shinde', 'Sanitation', '+919876543212'),
        (104, 'Manoj Verma', 'Plumbing (SDG 6)', '+919876543213'),
        (105, 'Vikas Patil', 'Electrical (SDG 12)', '+919876543214'),
        (106, 'Dinesh More', 'HVAC & Facility', '+919876543215'),
        (107, 'Sunil Jadhav', 'Plumbing (SDG 6)', '+919876543216'),
        (108, 'Pradeep Joshi', 'Electrical (SDG 12)', '+919876543217'),
    ]
    cursor.executemany(
        "INSERT INTO maintenance_staff (staff_id, name, specialization, contact_no) VALUES (?, ?, ?, ?)",
        staff_data
    )
    conn.commit()
    print(f"  -> Added {len(staff_data)} maintenance technicians.")

    conn.close()

    occupancy_pct = (target_student_count / 1800.0) * 100.0
    print("----------------------------------------------------------------")
    print("[SUCCESS] Complete Resident & Room Inventory Populated!")
    print(f"  * Blocks:        10 (Block-A to Block-J)")
    print(f"  * Floors/Block:  6 Floors")
    print(f"  * Rooms/Floor:   10 Rooms")
    print(f"  * Total Rooms:   600 Rooms")
    print(f"  * Total Beds:    1,800 Beds (Capacity: 3 per room)")
    print(f"  * Occupancy:     {target_student_count} / 1,800 Beds ({occupancy_pct:.1f}% Occupancy)")
    print(f"  * Utility Logs:  0 records (Ready for day-wise Auto-Sync)")
    print("================================================================")

if __name__ == "__main__":
    populate_database()
