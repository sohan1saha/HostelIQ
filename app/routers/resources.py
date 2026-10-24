from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.models.resource import WaterLogCreate, ElectricityLogCreate, TelemetrySimulationRequest
from app.models.student import StudentCreate, StudentTransferRequest
from app.database.sql_manager import sql_manager

router = APIRouter(prefix="/api/v1/resources", tags=["Resource & Data Management"])

class RoomCreate(BaseModel):
    block: str = Field(..., json_schema_extra={"example": "Block-C"})
    floor: int = Field(..., json_schema_extra={"example": 1})
    room_number: str = Field(..., json_schema_extra={"example": "C-101"})
    capacity: Optional[int] = Field(2, json_schema_extra={"example": 2})

@router.post("/student", status_code=status.HTTP_201_CREATED, summary="Register Resident Student")
def create_student(payload: StudentCreate):
    try:
        if payload.block and payload.room_number:
            room_id = sql_manager.validate_and_get_room_id(payload.block, payload.room_number)
        elif payload.room_id:
            room_id = payload.room_id
        else:
            room_id = 1

        student_id = sql_manager.add_student(
            student_id=payload.student_id,
            name=payload.name,
            email=payload.email,
            room_id=room_id
        )
        return {
            "status": "success",
            "message": "Student registered and allocated to room successfully",
            "student_id": payload.student_id,
            "allocated_room_id": room_id
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register student: {str(e)}")

@router.post("/students/transfer", summary="Reallocate Student to New Room")
def transfer_student(payload: StudentTransferRequest):
    """
    Room Transfer & Reallocation Wizard:
    Moves a student from their current room to a target room,
    strictly verifying target room capacity (< 3 beds occupied).
    """
    try:
        result = sql_manager.transfer_student(
            student_id=payload.student_id,
            new_room_id=payload.target_room_id
        )
        return {
            "status": "success",
            "message": f"Successfully transferred student {result['student_name']} ({result['student_id']}) to Room {result['new_room']}",
            "data": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

@router.post("/room", status_code=status.HTTP_201_CREATED, summary="Create Hostel Room")
def create_room(payload: RoomCreate):
    try:
        room_id = sql_manager.add_room(
            block=payload.block,
            floor=payload.floor,
            room_number=payload.room_number,
            capacity=payload.capacity or 2
        )
        return {
            "status": "success",
            "message": "Hostel room provisioned successfully",
            "room_id": room_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")

@router.post("/water-log", status_code=status.HTTP_201_CREATED, summary="Ingest Water Usage Log")
def log_water_consumption(payload: WaterLogCreate):
    try:
        log_id = sql_manager.add_water_log(
            room_id=payload.room_id,
            log_date=payload.log_date,
            water_used_liters=payload.water_used_liters,
            leak_flag=payload.leak_flag
        )
        return {
            "status": "success",
            "message": "Water telemetry reading recorded",
            "log_id": log_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record water telemetry: {str(e)}")

@router.post("/electricity-log", status_code=status.HTTP_201_CREATED, summary="Ingest Electricity Usage Log")
def log_electricity_consumption(payload: ElectricityLogCreate):
    try:
        log_id = sql_manager.add_electricity_log(
            room_id=payload.room_id,
            log_date=payload.log_date,
            kwh_consumed=payload.kwh_consumed,
            peak_usage_flag=payload.peak_usage_flag
        )
        return {
            "status": "success",
            "message": "Electricity telemetry reading recorded",
            "log_id": log_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record electricity telemetry: {str(e)}")

@router.get("/occupancy", summary="Hostel Occupancy & Capacity Metrics")
@router.get("/occupancy-stats", summary="Hostel Occupancy & Capacity Metrics Alias")
def get_occupancy_stats():
    try:
        return sql_manager.get_occupancy_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch occupancy stats: {str(e)}")

@router.get("/rooms", summary="List All Hostel Rooms")
def get_rooms():
    try:
        data = sql_manager.get_all_rooms()
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rooms: {str(e)}")

@router.get("/students", summary="List All Registered Students")
def get_students():
    try:
        data = sql_manager.get_all_students()
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch students: {str(e)}")

@router.get("/daywise-logs", summary="Get Day-wise Utility Telemetry Across All Rooms")
def get_daywise_logs(
    limit: int = 100,
    offset: int = 0,
    block: Optional[str] = None,
    floor: Optional[int] = None,
    room: Optional[str] = None,
    log_date: Optional[str] = None,
    anomaly_only: bool = False
):
    try:
        return sql_manager.get_daywise_telemetry_logs(
            limit=limit,
            offset=offset,
            block=block,
            floor=floor,
            room_number=room,
            log_date=log_date,
            anomaly_only=anomaly_only
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch day-wise telemetry logs: {str(e)}")

@router.post("/simulate-telemetry", status_code=status.HTTP_201_CREATED, summary="Simulate IoT Sensor Telemetry")
def simulate_telemetry(payload: Optional[TelemetrySimulationRequest] = None):
    try:
        target_date_str = str(payload.target_date) if payload and payload.target_date else None
        rate = payload.anomaly_rate if payload and payload.anomaly_rate is not None else 0.08
        result = sql_manager.simulate_telemetry_batch(target_date=target_date_str, anomaly_rate=rate)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate telemetry: {str(e)}")
