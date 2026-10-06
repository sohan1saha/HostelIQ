from fastapi import APIRouter, HTTPException, status
from app.models.resource import WaterLogCreate, ElectricityLogCreate
from app.database.sql_manager import sql_manager

router = APIRouter(prefix="/api/v1/resources", tags=["Resource Monitoring (SDG 6 & 12)"])

@router.post("/water-log", status_code=status.HTTP_201_CREATED, summary="Log Water Consumption (SDG 6)")
def log_water_consumption(payload: WaterLogCreate):
    """
    Log room water consumption in Liters and flag potential pipe leaks (SDG 6).
    Uses Pydantic validation for numeric boundaries.
    """
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
            "log_id": log_id,
            "sdg_target": "SDG 6: Clean Water & Sanitation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log water consumption: {str(e)}")

@router.post("/electricity-log", status_code=status.HTTP_201_CREATED, summary="Log Electricity Usage (SDG 12)")
def log_electricity_consumption(payload: ElectricityLogCreate):
    """
    Log room electricity consumption in kWh (SDG 12).
    Uses Pydantic validation for numeric boundaries.
    """
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
            "log_id": log_id,
            "sdg_target": "SDG 12: Responsible Consumption & Production"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log electricity usage: {str(e)}")
