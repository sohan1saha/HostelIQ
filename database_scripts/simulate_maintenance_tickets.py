#!/usr/bin/env python3
"""
HostelIQ - Maintenance Grievance Poisson Arrival Simulator
Simulates daily maintenance tickets based on mathematical queueing theory:
- Zero-Inflated Poisson Distribution P(k) = (lambda^k * e^-lambda) / k!
- Arrival rate lambda = N_occupied * mu_base * Volatility_Factor * Anomaly_Multiplier
- Enforces tickets < N_occupied (some days Nil (0), some days Moderate, some days Many)
"""

import sys
import os
import random
import math
from datetime import datetime, date

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.database.sql_manager import sql_manager
from app.database.nosql_manager import nosql_manager

GRIEVANCE_TEMPLATES = {
    "SDG 6 (Clean Water)": [
        ("Water Leakage", "Continuous tap leakage in bathroom causing water loss", "High"),
        ("Plumbing Issue", "Flush tank valve stuck and overflowing", "High"),
        ("Low Pressure", "Water supply pressure low in washbasin", "Medium"),
        ("Drainage", "Slow drainage in bathroom sink", "Low"),
    ],
    "SDG 12 (Energy)": [
        ("Electrical Spark", "Study lamp socket switch sparking occasionally", "High"),
        ("Power Tripping", "MCB circuit breaker tripped when running appliances", "High"),
        ("Appliance", "Ceiling fan regulator noisy and running only on high", "Medium"),
        ("Lighting", "Tube light flickering continuously in study area", "Low"),
    ],
    "Sanitation & Facility": [
        ("Sanitation", "Bathroom exhaust vent cleaning required", "Medium"),
        ("Pest Control", "Window mesh torn allowing mosquitoes inside", "Medium"),
        ("Carpentry", "Wardrobe hinge loose and door misaligned", "Low"),
    ]
}

def calculate_daily_ticket_target(occupied_count: int, leak_anomalies: int = 0, peak_anomalies: int = 0):
    """
    Mathematical arrival rate model:
    Zero-Inflated Inhomogeneous Poisson Process
    """
    if occupied_count <= 0:
        return 0, 0.0, "Zero Occupancy (Nil)"

    # Baseline daily grievance probability per occupied room (1.5% chance/day)
    mu_base = 0.015

    # Day volatility factor (Stochastic wave: draws from a discrete distribution)
    # 20% Nil probability, 55% Moderate probability, 25% Many probability
    day_volatility = random.choices(
        [0.0, 0.4, 0.8, 1.6, 2.4],
        weights=[0.20, 0.30, 0.25, 0.15, 0.10]
    )[0]

    # If day volatility is 0.0, it is a Zero-Incident Day (Nil)
    if day_volatility == 0.0:
        return 0, 0.0, "Nil (0 Tickets - Facility Optimal)"

    # Anomaly intensity ratio: active leaks or surges increase conditional failure rate moderately
    leak_ratio = leak_anomalies / occupied_count if occupied_count > 0 else 0.0
    peak_ratio = peak_anomalies / occupied_count if occupied_count > 0 else 0.0
    anomaly_factor = 1.0 + min(1.8, (2.0 * leak_ratio + 1.2 * peak_ratio))

    # Compute Poisson lambda parameter (mean arrival rate)
    lam = occupied_count * mu_base * day_volatility * anomaly_factor
    lam = max(0.5, lam)

    # Sample from Poisson distribution using Knuth's algorithm
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    k -= 1

    # Strict constraint: tickets MUST be strictly less than occupied rooms
    max_allowed = max(0, occupied_count - 1)
    k = min(k, max_allowed)

    # Determine classification label
    if k == 0:
        label = "Nil (0 Tickets - Quiet Day)"
    elif k <= 6:
        label = f"Moderate ({k} Tickets - Routine Flow)"
    else:
        label = f"Many ({k} Tickets - Surge Flow)"

    return k, round(lam, 2), label

def simulate_daily_tickets(target_date: str = None):
    print("================================================================")
    print("     HostelIQ - Stochastic Maintenance Grievance Simulator      ")
    print("================================================================")

    if not target_date:
        target_date = date.today().isoformat()

    # 1. Fetch Occupied Rooms and Assigned Students from SQL DB
    with sql_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.room_id, r.room_number, r.block, r.floor,
                   s.student_id, s.name as student_name
            FROM rooms r
            INNER JOIN students s ON r.room_id = s.room_id
            ORDER BY r.block, r.floor, r.room_number
        """)
        residents = [dict(row) for row in cursor.fetchall()]

        # Query recent anomalies from water and electricity
        cursor.execute("SELECT COUNT(*) FROM water_consumption WHERE log_date = ? AND leak_flag = 1", (target_date,))
        leak_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM electricity_consumption WHERE log_date = ? AND peak_usage_flag = 1", (target_date,))
        peak_count = cursor.fetchone()[0]

    if not residents:
        print("[!] No occupied rooms found in database. Please register residents first.")
        return {"status": "error", "message": "No occupied rooms found"}

    # Unique occupied rooms
    occupied_rooms = {}
    for res in residents:
        r_no = res["room_number"]
        if r_no not in occupied_rooms:
            occupied_rooms[r_no] = []
        occupied_rooms[r_no].append(res)

    occupied_count = len(occupied_rooms)

    # 2. Compute Ticket Count via Mathematical Poisson Model
    ticket_count, lam_val, classification = calculate_daily_ticket_target(
        occupied_count=occupied_count,
        leak_anomalies=leak_count,
        peak_anomalies=peak_count
    )

    print(f" [Mathematical Analysis]")
    print(f"  * Occupied Rooms Monitored (N):   {occupied_count} rooms")
    print(f"  * Mean Poisson Arrival Rate (lambda): {lam_val} tickets/day")
    print(f"  * Active Utility Anomalies:       {leak_count} water leaks | {peak_count} power surges")
    print(f"  * Daily Prediction / Outcome:     {classification}")
    print(f"  * Constraint Check:               {ticket_count} < {occupied_count} (Satisfied: STRICTLY LOWER)")
    print("----------------------------------------------------------------")

    if ticket_count == 0:
        print(" [RESULT] Zero maintenance tickets generated today (Facility optimal).")
        print("================================================================")
        return {
            "status": "success",
            "date": target_date,
            "occupied_rooms": occupied_count,
            "tickets_created": 0,
            "classification": classification,
            "lambda": lam_val,
            "tickets": []
        }

    # 3. Select random distinct occupied rooms for tickets
    selected_room_nos = random.sample(list(occupied_rooms.keys()), ticket_count)
    created_tickets = []

    for r_no in selected_room_nos:
        # Pick one resident from that room
        resident = random.choice(occupied_rooms[r_no])

        # Pick grievance category
        category_group = random.choices(
            ["SDG 6 (Clean Water)", "SDG 12 (Energy)", "Sanitation & Facility"],
            weights=[0.45, 0.40, 0.15]
        )[0]
        cat, desc, priority = random.choice(GRIEVANCE_TEMPLATES[category_group])

        # SDG target string
        sdg_target = "SDG 6" if "Water" in category_group else ("SDG 12" if "Energy" in category_group else "SDG 11")

        complaint_payload = {
            "student_id": resident["student_id"],
            "student_name": resident["student_name"],
            "room_number": r_no,
            "category": cat,
            "sdg_target": sdg_target,
            "description": desc,
            "priority": priority,
            "created_at": target_date
        }

        # Store in NoSQL document engine
        doc = nosql_manager.create_complaint(complaint_payload)
        created_tickets.append(doc)

        print(f"  + Ticket {doc.get('complaint_id', 'CMP')} | Room {r_no:<6} | {cat:<16} | [{priority:<6}] -> {resident['student_name']} | Tech: {doc.get('assigned_staff_name')} | SLA: {doc.get('sla_deadline_hours')}h")

    print("----------------------------------------------------------------")
    print(f" [SUCCESS] Successfully registered {len(created_tickets)} grievances in NoSQL Database!")
    print(f"  * All tickets stored with student allocations & resolution status.")
    print("================================================================")

    return {
        "status": "success",
        "date": target_date,
        "occupied_rooms": occupied_count,
        "tickets_created": len(created_tickets),
        "classification": classification,
        "lambda": lam_val,
        "tickets": created_tickets
    }

if __name__ == "__main__":
    simulate_daily_tickets()
