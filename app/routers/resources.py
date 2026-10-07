from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.models.resource import WaterLogCreate, ElectricityLogCreate
from app.models.student import StudentCreate
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
        student_id = sql_manager.add_student(
            student_id=payload.student_id,
            name=payload.name,
            email=payload.email,
            room_id=payload.room_id or 1
        )
        return {
            "status": "success",
            "message": "Student registered successfully",
            "student_id": payload.student_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register student: {str(e)}")

@router.post("/room", status_code=status.HTTP_201_CREATED, summary="Add Room Inventory")
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
            "message": "Room added successfully",
            "room_id": room_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add room: {str(e)}")

@router.post("/water-log", status_code=status.HTTP_201_CREATED, summary="Log Water Consumption")
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
            "message": "Water consumption logged successfully",
            "log_id": log_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log water consumption: {str(e)}")

@router.post("/electricity-log", status_code=status.HTTP_201_CREATED, summary="Log Electricity Usage")
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
            "message": "Electricity consumption logged successfully",
            "log_id": log_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log electricity usage: {str(e)}")
