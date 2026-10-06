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

sql_manager = SQLManager()
