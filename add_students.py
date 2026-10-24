#!/usr/bin/env python3
"""
HostelIQ - Resident Population Setup
Asks how many students to register out of the potential 1,800 capacity.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database_scripts.populate_full_hostel import populate_database

def main():
    print("""
    +-------------------------------------------------------------+
    |             HostelIQ - Resident Population Setup            |
    |      Total Capacity: 10 Blocks | 600 Rooms | 1,800 Beds     |
    +-------------------------------------------------------------+
    """)

    parser = argparse.ArgumentParser(description="Populate students into HostelIQ database")
    parser.add_argument("--count", type=int, default=None, help="Number of students to populate (1 to 1800)")
    args, _ = parser.parse_known_args()

    count = args.count

    if count is None:
        while True:
            try:
                prompt_msg = "  >> How many students do you want to register? [1 - 1800] (Press Enter for 1800): "
                user_val = input(prompt_msg).strip()
                if not user_val:
                    count = 1800
                    break
                count = int(user_val)
                if 1 <= count <= 1800:
                    break
                else:
                    print("  [!] Please enter a number between 1 and 1800.")
            except (ValueError, KeyboardInterrupt):
                print("\n  [!] Exiting.")
                return

    print(f"\n[*] Provisioning 600 rooms and registering {count} students...")
    populate_database(target_student_count=count)

if __name__ == "__main__":
    main()
