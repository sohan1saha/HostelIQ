from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TimelineEntry(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "Submitted"})
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FeedbackModel(BaseModel):
    rating: int = Field(..., ge=1, le=5, json_schema_extra={"example": 5}, description="1 to 5 stars rating")
    comments: Optional[str] = Field(None, json_schema_extra={"example": "Resolved quickly!"})

class ComplaintCreate(BaseModel):
    student_id: str = Field(..., json_schema_extra={"example": "STU2025001"})
    room_number: str = Field(..., json_schema_extra={"example": "A-101"})
    category: str = Field(..., json_schema_extra={"example": "Water Leakage"}, description="Category: Water Leakage (SDG 6), Electrical (SDG 12), Sanitation")
    sdg_target: str = Field("SDG 6", json_schema_extra={"example": "SDG 6"})
    description: str = Field(..., json_schema_extra={"example": "Pipe leaking under sink"})
    priority: str = Field("Medium", json_schema_extra={"example": "High"})

class ComplaintStatusUpdate(BaseModel):
    complaint_id: str
    status: str = Field(..., json_schema_extra={"example": "In Progress"})
    assigned_staff_id: Optional[int] = Field(None, json_schema_extra={"example": 101})

class ComplaintFeedbackUpdate(BaseModel):
    complaint_id: str
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
