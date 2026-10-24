#!/usr/bin/env python3
"""
HostelIQ - IoT Sensor & Smart Sub-Meter Simulator
Simulates hardware telemetry from ESP32 / LoRaWAN edge gateway devices:
- Smart Water Flow Meters (SDG 6)
- Digital Energy Sub-Meters (SDG 12)
- Edge Anomaly Detection (Pipe Leaks & Peak Power Surges)

Usage:
  python iot_simulator.py               # Ingests telemetry for all rooms for today
  python iot_simulator.py --days 7      # Backfills telemetry for the past 7 days
  python iot_simulator.py --stream 5    # Continuously streams telemetry every 5 seconds
"""

import sys
import time
import argparse
from datetime import date, timedelta

# Ensure project root is in sys.path
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.sql_manager import sql_manager

def run_simulation_for_date(target_date_str: str, anomaly_rate: float = 0.08):
    print(f"\n=======================================================")
    print(f" [IoT GATEWAY] Transmitting Sensor Telemetry for: {target_date_str}")
    print(f"=======================================================")
    
    result = sql_manager.simulate_telemetry_batch(target_date=target_date_str, anomaly_rate=anomaly_rate)
    
    if result.get("status") == "error":
        print(f"[ERROR] {result.get('message')}")
        return False
        
    readings = result.get("readings", [])
    for r in readings:
        leak_indicator = "ALERT: LEAK (SDG 6)" if r["leak_flag"] else "OK"
        peak_indicator = "ALERT: PEAK SURGE (SDG 12)" if r["peak_flag"] else "OK"
        
        print(f"  [Room {r['room_number']:<6}] Occupants: {r['occupants']} | "
              f"Water: {r['water_liters']:>5.1f} L [{leak_indicator:<20}] | "
              f"Energy: {r['electricity_kwh']:>4.1f} kWh [{peak_indicator}]")
              
    print(f"-------------------------------------------------------")
    print(f" Summary: {result['rooms_logged']} Meters Polled | "
          f"{result['leaks_detected']} Water Leaks | "
          f"{result['peak_surges_detected']} Power Surges")
    print(f" Ingestion Status: COMPLETED (Written to SQL Database)")
    return True

def main():
    parser = argparse.ArgumentParser(description="HostelIQ IoT Smart Meter Telemetry Simulator")
    parser.add_argument("--days", type=int, default=1, help="Number of past days to simulate (default: 1)")
    parser.add_argument("--anomaly-rate", type=float, default=0.08, help="Probability of leak / surge anomaly (0.0 to 1.0, default: 0.08)")
    parser.add_argument("--stream", type=int, default=0, help="Stream interval in seconds (e.g. --stream 5 for continuous pulses)")
    args = parser.parse_args()

    print("""
    +-------------------------------------------------------+
    |           HostelIQ IoT Smart Meter Simulator          |
    |      Telemetry Ingestion for Water & Electricity      |
    +-------------------------------------------------------+
    """)

    if args.stream > 0:
        print(f"[*] Starting live continuous IoT streaming (Interval: {args.stream}s). Press Ctrl+C to stop.")
        cycle = 1
        try:
            while True:
                today_str = date.today().isoformat()
                print(f"\n--- [Telemetry Pulse #{cycle}] ---")
                run_simulation_for_date(today_str, anomaly_rate=args.anomaly_rate)
                cycle += 1
                time.sleep(args.stream)
        except KeyboardInterrupt:
            print("\n[!] IoT Streaming stopped by user.")
            return

    # Batch / Day simulation
    today = date.today()
    for d in range(args.days - 1, -1, -1):
        target_dt = today - timedelta(days=d)
        run_simulation_for_date(target_dt.isoformat(), anomaly_rate=args.anomaly_rate)

if __name__ == "__main__":
    main()
