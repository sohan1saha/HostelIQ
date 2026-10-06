from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class WaterLogCreate(BaseModel):
    room_id: int = Field(..., json_schema_extra={"example": 1}, description="Target Room ID")
    log_date: date = Field(..., json_schema_extra={"example": "2026-10-06"}, description="Log Date")
    water_used_liters: float = Field(..., gt=0, json_schema_extra={"example": 180.5}, description="Water consumed in Liters (SDG 6)")
    leak_flag: Optional[int] = Field(0, json_schema_extra={"example": 0}, description="1 if unusual flow detected, 0 otherwise")

class ElectricityLogCreate(BaseModel):
    room_id: int = Field(..., json_schema_extra={"example": 1}, description="Target Room ID")
    log_date: date = Field(..., json_schema_extra={"example": "2026-10-06"}, description="Log Date")
    kwh_consumed: float = Field(..., gt=0, json_schema_extra={"example": 14.2}, description="Electricity consumed in kWh (SDG 12)")
    peak_usage_flag: Optional[int] = Field(0, json_schema_extra={"example": 0}, description="1 if peak hour usage exceeded threshold")

class HighConsumptionQueryParam(BaseModel):
    threshold_liters: float = Field(300.0, description="Water usage threshold in Liters to flag rooms")
