#!/usr/bin/env python3
"""
HostelIQ - One-Click Database Wipe
Deletes all records from hosteliq.db (rooms, students, staff, water & electricity logs).
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database_scripts.reset_db import empty_database

if __name__ == "__main__":
    empty_database()
