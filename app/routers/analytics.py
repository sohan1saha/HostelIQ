from fastapi import APIRouter, Query, HTTPException
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
