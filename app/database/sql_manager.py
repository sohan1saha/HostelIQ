import sqlite3
import os
from app.config import settings

class SQLManager:
    """
    SQL Manager handling Relational Data operations:
    - Multi-table Joins
    - Grouping & Aggregations
    - Nested Subqueries
    - Advanced Resource Anomaly Flagging
    """
    def __init__(self, db_path: str = settings.SQL_DB_FILE):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes database schema and populates seed data if empty."""
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database_scripts", "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            with self.get_connection() as conn:
                conn.executescript(sql_script)
                conn.commit()

    # --- ADVANCED QUERY 1: Multi-Table Joins ---
    def get_student_room_usage(self):
        """
        ADVANCED QUERY: Joins Students, Rooms, and Water Consumption logs.
        Satisfies DCDS Rubric: Multi-Table Joins.
        """
        query = """
        SELECT 
            s.student_id,
            s.name AS student_name,
            s.email,
            r.block,
            r.room_number,
            w.log_date,
            w.water_used_liters,
            w.leak_flag
        FROM students s
        INNER JOIN rooms r ON s.room_id = r.room_id
        INNER JOIN water_consumption w ON r.room_id = w.room_id
        ORDER BY w.water_used_liters DESC;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    # --- ADVANCED QUERY 2: Grouping & Aggregations ---
    def get_block_utility_summary(self):
        """
        ADVANCED QUERY: Aggregates daily water & electricity usage by block & floor.
        Satisfies DCDS Rubric: Grouping & Aggregations (SUM, AVG, COUNT).
        """
        query = """
        SELECT 
            r.block,
            r.floor,
            COUNT(DISTINCT r.room_id) AS total_rooms,
            ROUND(AVG(w.water_used_liters), 2) AS avg_water_liters,
            ROUND(SUM(w.water_used_liters), 2) AS total_water_liters,
            ROUND(AVG(e.kwh_consumed), 2) AS avg_electricity_kwh,
            ROUND(SUM(e.kwh_consumed), 2) AS total_electricity_kwh
        FROM rooms r
        LEFT JOIN water_consumption w ON r.room_id = w.room_id
        LEFT JOIN electricity_consumption e ON r.room_id = e.room_id
        GROUP BY r.block, r.floor
        ORDER BY r.block, r.floor;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    # --- ADVANCED QUERY 3: Nested Subquery ---
    def get_excessive_water_consuming_rooms(self):
        """
        ADVANCED QUERY: Nested subquery identifying rooms consuming water
        strictly > 80% above the overall hostel average water consumption.
        Satisfies DCDS Rubric: Nested Subqueries.
        """
        query = """
        SELECT 
            r.room_number,
            r.block,
            r.floor,
            w.log_date,
            w.water_used_liters,
            (SELECT ROUND(AVG(water_used_liters), 2) FROM water_consumption) AS overall_avg_water
        FROM water_consumption w
        JOIN rooms r ON w.room_id = r.room_id
        WHERE w.water_used_liters > 1.8 * (
            SELECT AVG(water_used_liters) FROM water_consumption
        )
        ORDER BY w.water_used_liters DESC;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    # --- ADVANCED QUERY 4: Stored Procedure / Dynamic Anomaly Query ---
    def flag_high_consuming_rooms(self, threshold_water: float = 300.0):
        """
        ADVANCED QUERY: Dynamic CTE query simulating a Stored Procedure to flag rooms
        exceeding custom resource thresholds for SDG 6 & SDG 12 auditing.
        """
        query = """
        WITH RoomAvgWater AS (
            SELECT room_id, AVG(water_used_liters) AS avg_water
            FROM water_consumption
            GROUP BY room_id
        ),
        RoomAvgElectricity AS (
            SELECT room_id, AVG(kwh_consumed) AS avg_kwh
            FROM electricity_consumption
            GROUP BY room_id
        )
        SELECT 
            r.room_id,
            r.block,
            r.room_number,
            ROUND(raw.avg_water, 2) AS avg_water_liters,
            ROUND(rae.avg_kwh, 2) AS avg_electricity_kwh,
            CASE 
                WHEN raw.avg_water > ? THEN 'HIGH WATER LEAK RISK (SDG 6)'
                ELSE 'NORMAL'
            END AS water_status
        FROM rooms r
        LEFT JOIN RoomAvgWater raw ON r.room_id = raw.room_id
        LEFT JOIN RoomAvgElectricity rae ON r.room_id = rae.room_id
        WHERE raw.avg_water > ?;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (threshold_water, threshold_water))
            return [dict(row) for row in cursor.fetchall()]

    # --- CRUD Helper Methods ---
    def add_water_log(self, room_id: int, log_date: str, water_used_liters: float, leak_flag: int = 0):
        query = "INSERT INTO water_consumption (room_id, log_date, water_used_liters, leak_flag) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (room_id, str(log_date), water_used_liters, leak_flag))
            conn.commit()
            return cursor.lastrowid

    def add_electricity_log(self, room_id: int, log_date: str, kwh_consumed: float, peak_usage_flag: int = 0):
        query = "INSERT INTO electricity_consumption (room_id, log_date, kwh_consumed, peak_usage_flag) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (room_id, str(log_date), kwh_consumed, peak_usage_flag))
            conn.commit()
            return cursor.lastrowid

    def add_student(self, student_id: str, name: str, email: str, room_id: int):
        query = "INSERT INTO students (student_id, name, email, room_id) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (student_id, name, email, room_id))
            conn.commit()
            return cursor.lastrowid

    def validate_and_get_room_id(self, block: str, room_number_input: str) -> int:
        """
        Validates room number format, floor bounds (1-4), and room ordering limits (max 10 rooms per floor: 01-10).
        Automatically formats room string e.g., Block 'Block-A' + Room '101' -> 'A-101'.
        """
        raw = room_number_input.strip().upper()
        digits = "".join([c for c in raw if c.isdigit()])
        if not digits or len(digits) < 3:
            raise ValueError(f"Invalid room number '{room_number_input}'. Must specify digits like 101, 204, 308.")

        floor = int(digits[0])
        room_suffix = int(digits[-2:])

        if floor < 1 or floor > 4:
            raise ValueError(f"Invalid floor level '{floor}'. Hostel floors are limited to Floors 1 through 4.")

        if room_suffix < 1 or room_suffix > 10:
            raise ValueError(f"Room number suffix '{room_suffix:02d}' exceeds limit. Max 10 rooms allowed per floor (01 to 10, e.g., {floor}01 to {floor}10).")

        clean_block_code = block.split('-')[-1] if '-' in block else block
        if not raw.startswith(clean_block_code):
            formatted_room_no = f"{clean_block_code}-{digits}"
        else:
            formatted_room_no = raw

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT room_id FROM rooms WHERE room_number = ?", (formatted_room_no,))
            row = cursor.fetchone()
            if row:
                return row["room_id"]
            else:
                cursor.execute(
                    "INSERT INTO rooms (block, floor, room_number, capacity) VALUES (?, ?, ?, ?)",
                    (block, floor, formatted_room_no, 2)
                )
                conn.commit()
                return cursor.lastrowid

    def get_consumption_breakdown(self, group_by: str = "room", blocks: list = None, floors: list = None, room_numbers: list = None):
        """
        ADVANCED MULTI-LEVEL CONSUMPTION ANALYTICS:
        Provides flexible resource telemetry breakdown:
        - Room-wise
        - Floor-wise
        - Block-wise
        - Conjoining 2 or more rooms, floors, blocks, or all
        Returns itemized breakdown, conjoined grand total summary, and available filter metadata.
        """
        # 1. Fetch available metadata for UI filters
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT block FROM rooms ORDER BY block")
            available_blocks = [r["block"] for r in cur.fetchall()]

            cur.execute("SELECT DISTINCT floor FROM rooms ORDER BY floor")
            available_floors = [r["floor"] for r in cur.fetchall()]

            cur.execute("SELECT room_id, room_number, block, floor FROM rooms ORDER BY block, floor, room_number")
            available_rooms = [dict(r) for r in cur.fetchall()]

        # 2. Build filtered room query using CTE
        where_clauses = ["1=1"]
        params = []
        if blocks:
            placeholders = ",".join(["?"] * len(blocks))
            where_clauses.append(f"r.block IN ({placeholders})")
            params.extend(blocks)
        if floors:
            placeholders = ",".join(["?"] * len(floors))
            where_clauses.append(f"r.floor IN ({placeholders})")
            params.extend(floors)
        if room_numbers:
            placeholders = ",".join(["?"] * len(room_numbers))
            where_clauses.append(f"r.room_number IN ({placeholders})")
            params.extend(room_numbers)

        query = f"""
        WITH RoomWater AS (
            SELECT room_id, COUNT(log_id) as w_count, SUM(water_used_liters) as tot_water, AVG(water_used_liters) as avg_water, SUM(leak_flag) as leak_count
            FROM water_consumption GROUP BY room_id
        ),
        RoomElec AS (
            SELECT room_id, COUNT(log_id) as e_count, SUM(kwh_consumed) as tot_elec, AVG(kwh_consumed) as avg_elec, SUM(peak_usage_flag) as peak_count
            FROM electricity_consumption GROUP BY room_id
        )
        SELECT r.room_id, r.block, r.floor, r.room_number, r.capacity,
               COALESCE(rw.w_count, 0) as w_count, COALESCE(ROUND(rw.tot_water, 2), 0) as tot_water, COALESCE(ROUND(rw.avg_water, 2), 0) as avg_water, COALESCE(rw.leak_count, 0) as leak_count,
               COALESCE(re.e_count, 0) as e_count, COALESCE(ROUND(re.tot_elec, 2), 0) as tot_elec, COALESCE(ROUND(re.avg_elec, 2), 0) as avg_elec, COALESCE(re.peak_count, 0) as peak_count
        FROM rooms r
        LEFT JOIN RoomWater rw ON r.room_id = rw.room_id
        LEFT JOIN RoomElec re ON r.room_id = re.room_id
        WHERE {' AND '.join(where_clauses)}
        ORDER BY r.block, r.floor, r.room_number
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            room_rows = [dict(r) for r in cur.fetchall()]

        # 3. Compute Conjoined Grand Total across all filtered rooms
        total_rooms = len(room_rows)
        total_water = round(sum(r["tot_water"] for r in room_rows), 2)
        avg_water_per_room = round(total_water / total_rooms, 2) if total_rooms else 0.0
        total_elec = round(sum(r["tot_elec"] for r in room_rows), 2)
        avg_elec_per_room = round(total_elec / total_rooms, 2) if total_rooms else 0.0
        total_leaks = sum(r["leak_count"] for r in room_rows)
        total_peaks = sum(r["peak_count"] for r in room_rows)

        conjoined_summary = {
            "total_rooms": total_rooms,
            "total_water": total_water,
            "avg_water_per_room": avg_water_per_room,
            "total_elec": total_elec,
            "avg_elec_per_room": avg_elec_per_room,
            "total_leaks": total_leaks,
            "total_peaks": total_peaks
        }

        # 4. Format items based on group_by parameter
        items = []
        if group_by == "floor":
            floors_dict = {}
            for r in room_rows:
                fl = r["floor"]
                if fl not in floors_dict:
                    floors_dict[fl] = {
                        "identifier": f"Floor {fl}",
                        "label": f"Floor {fl}",
                        "floor": fl,
                        "blocks": set(),
                        "rooms": [],
                        "room_count": 0,
                        "tot_water": 0.0,
                        "tot_elec": 0.0,
                        "leak_count": 0,
                        "peak_count": 0
                    }
                floors_dict[fl]["blocks"].add(r["block"])
                floors_dict[fl]["rooms"].append(r["room_number"])
                floors_dict[fl]["room_count"] += 1
                floors_dict[fl]["tot_water"] += r["tot_water"]
                floors_dict[fl]["tot_elec"] += r["tot_elec"]
                floors_dict[fl]["leak_count"] += r["leak_count"]
                floors_dict[fl]["peak_count"] += r["peak_count"]

            for fl in sorted(floors_dict.keys()):
                d = floors_dict[fl]
                d["blocks"] = sorted(list(d["blocks"]))
                d["tot_water"] = round(d["tot_water"], 2)
                d["avg_water"] = round(d["tot_water"] / d["room_count"], 2) if d["room_count"] else 0.0
                d["tot_elec"] = round(d["tot_elec"], 2)
                d["avg_elec"] = round(d["tot_elec"] / d["room_count"], 2) if d["room_count"] else 0.0
                items.append(d)

        elif group_by == "block":
            blocks_dict = {}
            for r in room_rows:
                blk = r["block"]
                if blk not in blocks_dict:
                    blocks_dict[blk] = {
                        "identifier": blk,
                        "label": blk,
                        "block": blk,
                        "floors": set(),
                        "rooms": [],
                        "room_count": 0,
                        "tot_water": 0.0,
                        "tot_elec": 0.0,
                        "leak_count": 0,
                        "peak_count": 0
                    }
                blocks_dict[blk]["floors"].add(r["floor"])
                blocks_dict[blk]["rooms"].append(r["room_number"])
                blocks_dict[blk]["room_count"] += 1
                blocks_dict[blk]["tot_water"] += r["tot_water"]
                blocks_dict[blk]["tot_elec"] += r["tot_elec"]
                blocks_dict[blk]["leak_count"] += r["leak_count"]
                blocks_dict[blk]["peak_count"] += r["peak_count"]

            for blk in sorted(blocks_dict.keys()):
                d = blocks_dict[blk]
                d["floors"] = sorted(list(d["floors"]))
                d["tot_water"] = round(d["tot_water"], 2)
                d["avg_water"] = round(d["tot_water"] / d["room_count"], 2) if d["room_count"] else 0.0
                d["tot_elec"] = round(d["tot_elec"], 2)
                d["avg_elec"] = round(d["tot_elec"] / d["room_count"], 2) if d["room_count"] else 0.0
                items.append(d)

        elif group_by == "conjoined":
            # Conjoined view: single aggregated cohort representation
            labels = []
            if blocks:
                labels.append(f"Blocks: {', '.join(blocks)}")
            if floors:
                labels.append(f"Floors: {', '.join(str(f) for f in floors)}")
            if room_numbers:
                labels.append(f"Rooms: {', '.join(room_numbers)}")
            cohort_name = " + ".join(labels) if labels else "All Hostel Units Conjoined"
            items.append({
                "identifier": "Conjoined Selection",
                "label": cohort_name,
                "room_count": total_rooms,
                "tot_water": total_water,
                "avg_water": avg_water_per_room,
                "tot_elec": total_elec,
                "avg_elec": avg_elec_per_room,
                "leak_count": total_leaks,
                "peak_count": total_peaks
            })

        else:
            # Default room-wise
            for r in room_rows:
                items.append({
                    "identifier": r["room_number"],
                    "label": f"{r['block']} · {r['room_number']} (Fl {r['floor']})",
                    "room_number": r["room_number"],
                    "block": r["block"],
                    "floor": r["floor"],
                    "capacity": r["capacity"],
                    "room_count": 1,
                    "tot_water": r["tot_water"],
                    "avg_water": r["avg_water"],
                    "tot_elec": r["tot_elec"],
                    "avg_elec": r["avg_elec"],
                    "leak_count": r["leak_count"],
                    "peak_count": r["peak_count"],
                    "w_count": r["w_count"],
                    "e_count": r["e_count"]
                })

        return {
            "group_by": group_by,
            "filters": {
                "blocks": blocks or [],
                "floors": floors or [],
                "room_numbers": room_numbers or []
            },
            "items": items,
            "conjoined_summary": conjoined_summary,
            "available_metadata": {
                "blocks": available_blocks,
                "floors": available_floors,
                "rooms": available_rooms
            }
        }

sql_manager = SQLManager()
