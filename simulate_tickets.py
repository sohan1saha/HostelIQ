#!/usr/bin/env python3
"""
HostelIQ - Maintenance Grievance Poisson Arrival Simulator
Simulates daily maintenance tickets based on mathematical queueing theory:
- Zero-Inflated Inhomogeneous Poisson Process
- Strictly lower than occupied room count (k < N_occupied)
- Categorizes complaints into SDG 6 (Water), SDG 12 (Energy), and Sanitation
"""

import sys
import os
import argparse
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database_scripts.simulate_maintenance_tickets import simulate_daily_tickets

def main():
    parser = argparse.ArgumentParser(description="Simulate daily maintenance grievances for HostelIQ")
    parser.add_argument("--date", type=str, default=None, help="Target date in YYYY-MM-DD format (defaults to today)")
    args = parser.parse_args()

    target_date = args.date or date.today().isoformat()
    simulate_daily_tickets(target_date=target_date)

if __name__ == "__main__":
    main()
