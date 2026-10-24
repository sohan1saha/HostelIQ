import io
import csv
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.database.sql_manager import sql_manager
from app.database.nosql_manager import nosql_manager

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Advanced Queries"])

@router.get("/multi-table-join", summary="SQL Join: Student Room Utility Usage")
def get_student_room_usage():
    """
    Rubric Requirement: Advanced Database Querying (Multi-Table Joins)
    Executes a 3-way SQL INNER JOIN across Students, Rooms, and Water Consumption logs.
    """
    try:
        data = sql_manager.get_student_room_usage()
        return {
            "query_type": "3-Way SQL INNER JOIN (Students + Rooms + Water Consumption)",
            "record_count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL Join Query Failed: {str(e)}")

@router.get("/block-summary", summary="SQL Aggregations & Grouping")
def get_block_utility_summary():
    """
    Rubric Requirement: Advanced Database Querying (Grouping & Aggregations)
    Aggregates water and electricity usage grouped by hostel block and floor.
    """
    try:
        data = sql_manager.get_block_utility_summary()
        return {
            "query_type": "SQL Aggregation & GROUP BY (Block & Floor)",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL Aggregation Query Failed: {str(e)}")

@router.get("/excessive-water-rooms", summary="SQL Nested Subquery: Excessive Water Consumption")
def get_excessive_water_consuming_rooms():
    """
    Rubric Requirement: Advanced Database Querying (Nested Subqueries)
    Finds rooms with water usage > 80% above the hostel average.
    """
    try:
        data = sql_manager.get_excessive_water_consuming_rooms()
        return {
            "query_type": "Nested SQL Subquery (> 1.8x Average Water Usage)",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL Subquery Failed: {str(e)}")

@router.get("/flagged-high-consumption", summary="SQL Stored Procedure / Anomaly Query")
def flag_high_consuming_rooms(threshold: float = Query(300.0, description="Threshold Liters")):
    """
    Rubric Requirement: Advanced Database Querying (Stored Procedure / CTE)
    Flags rooms exceeding specific water thresholds for SDG 6 monitoring.
    """
    try:
        data = sql_manager.flag_high_consuming_rooms(threshold_water=threshold)
        return {
            "query_type": "SQL Stored Procedure Simulation (CTE High Resource Anomaly Flagging)",
            "threshold_liters": threshold,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stored Procedure Execution Failed: {str(e)}")

@router.get("/mongo-pipeline", summary="NoSQL MongoDB Aggregation Pipeline")
def get_mongo_aggregation_analytics():
    """
    Rubric Requirement: Advanced Database Querying (MongoDB Aggregation Pipeline)
    Executes a multi-stage MongoDB pipeline ($match, $group, $project, $sort).
    """
    try:
        data = nosql_manager.get_complaint_analytics_pipeline()
        return {
            "query_type": "MongoDB Aggregation Pipeline ($match -> $group -> $project -> $sort)",
            "database": "MongoDB / NoSQL Document Engine",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB Aggregation Failed: {str(e)}")

@router.get("/consumption-breakdown", summary="Multi-Level Consumption Analytics (Room, Floor, Block, Conjoined)")
def get_consumption_breakdown(
    group_by: str = Query("room", description="Granularity: 'room' | 'floor' | 'block' | 'conjoined'"),
    blocks: str = Query(None, description="Comma-separated blocks e.g. Block-A,Block-B"),
    floors: str = Query(None, description="Comma-separated floor numbers e.g. 1,2"),
    rooms: str = Query(None, description="Comma-separated room numbers e.g. A-101,B-101")
):
    try:
        block_list = [b.strip() for b in blocks.split(",") if b.strip()] if blocks else None
        floor_list = [int(f.strip()) for f in floors.split(",") if f.strip() and f.strip().isdigit()] if floors else None
        room_list = [r.strip() for r in rooms.split(",") if r.strip()] if rooms else None

        data = sql_manager.get_consumption_breakdown(
            group_by=group_by,
            blocks=block_list,
            floors=floor_list,
            room_numbers=room_list
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch consumption breakdown: {str(e)}")

@router.get("/floor-heatmap", summary="Interactive 2D Floor Heatmap Grid")
def get_floor_heatmap(
    block: str = Query("Block-A", description="Hostel Block (e.g. Block-A)"),
    floor: int = Query(1, ge=1, le=6, description="Floor level (1-6)"),
    date: Optional[str] = Query(None, description="Target date (YYYY-MM-DD)")
):
    """
    Returns 2D grid matrix of rooms color-coded dynamically:
    - Green (Optimal)
    - Amber (Elevated usage)
    - Red (Active Leak or Peak Surge)
    - Grey (Vacant)
    """
    try:
        return sql_manager.get_floor_heatmap(block=block, floor=floor, target_date=date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap retrieval failed: {str(e)}")

@router.get("/forecast", summary="7-Day Predictive Resource Demand Forecast (EWMA & Trend)")
def get_resource_forecast(days: int = Query(7, ge=1, le=30, description="Forecast horizon in days")):
    """
    Applies Exponential Weighted Moving Averages (EWMA) and Holt's trend extrapolation
    to predict the next 7 days of Water and Electricity consumption.
    """
    try:
        return sql_manager.get_resource_forecast(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast calculation failed: {str(e)}")

@router.get("/eco-scorecard", summary="ESG Sustainability & Eco-Rating Scorecard")
def get_eco_scorecard():
    """
    ESG Conservation Scorecard:
    - Converts kWh into kg CO2e emissions (0.82 kg CO2e / kWh)
    - Calculates municipal cost savings from resolved water leaks
    - Assigns Eco-Ratings (A+ to F) to Blocks based on per-capita conservation
    """
    try:
        return sql_manager.get_eco_scorecard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scorecard generation failed: {str(e)}")

# --- ONE-CLICK CSV AUDIT EXPORTERS ---

@router.get("/export/daywise-telemetry", summary="Export Daywise Telemetry to CSV")
def export_daywise_telemetry():
    """
    Streams clean CSV audit log of daywise telemetry across all rooms.
    """
    try:
        result = sql_manager.get_daywise_telemetry_logs(limit=5000)
        logs = result.get("data", [])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Log Date", "Room Number", "Block", "Floor", "Occupancy",
            "Water Used (Liters)", "Water Leak Flag",
            "Electricity Consumed (kWh)", "Peak Surge Flag", "Anomaly Detected"
        ])
        for row in logs:
            writer.writerow([
                row.get("log_date"),
                row.get("room_number"),
                row.get("block"),
                row.get("floor"),
                row.get("occupancy"),
                row.get("water_liters"),
                "YES" if row.get("leak_flag") else "NO",
                row.get("electricity_kwh"),
                "YES" if row.get("peak_flag") else "NO",
                "YES" if row.get("has_anomaly") else "NO"
            ])
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=hosteliq_daywise_telemetry.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")

@router.get("/export/residents", summary="Export Resident Roster to CSV")
def export_residents():
    """
    Streams clean CSV roster of all registered student residents with room allocations.
    """
    try:
        students = sql_manager.get_all_students()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Student ID", "Student Name", "Institutional Email", "Hostel Block", "Room Number"])
        for s in students:
            writer.writerow([
                s.get("student_id"),
                s.get("student_name"),
                s.get("email"),
                s.get("block"),
                s.get("room_number")
            ])
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=hosteliq_resident_roster.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Residents export failed: {str(e)}")

@router.get("/export/grievances", summary="Export Grievance & Maintenance Log to CSV")
def export_grievances():
    """
    Streams clean CSV audit log of all maintenance tickets, technician allocations, and SLA states.
    """
    try:
        complaints = nosql_manager.get_all_complaints()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Ticket ID", "Student ID", "Room Number", "Category", "SDG Target",
            "Description", "Priority", "Status", "Assigned Technician",
            "Technician Trade", "Contact", "SLA Hours", "SLA Status"
        ])
        for c in complaints:
            writer.writerow([
                c.get("complaint_id"),
                c.get("student_id"),
                c.get("room_number"),
                c.get("category"),
                c.get("sdg_target"),
                c.get("description"),
                c.get("priority"),
                c.get("status"),
                c.get("assigned_staff_name", "Unassigned"),
                c.get("assigned_staff_trade", "General"),
                c.get("assigned_staff_phone", "N/A"),
                c.get("sla_deadline_hours", "N/A"),
                c.get("sla_status", "Within SLA")
            ])
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=hosteliq_maintenance_tickets.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grievances export failed: {str(e)}")
