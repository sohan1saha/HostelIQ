from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class StudentBase(BaseModel):
    student_id: str = Field(..., json_schema_extra={"example": "STU2025001"}, description="Unique Student ID")
    name: str = Field(..., json_schema_extra={"example": "Aarav Sharma"}, description="Full Name")
    email: EmailStr = Field(..., json_schema_extra={"example": "aarav.sharma@sitpune.edu.in"}, description="SIT Pune Email")
    block: Optional[str] = Field("Block-A", json_schema_extra={"example": "Block-A"}, description="Hostel Block")
    room_number: Optional[str] = Field("101", json_schema_extra={"example": "101"}, description="Room Number (e.g. 101-110, 201-210)")
    room_id: Optional[int] = Field(None, json_schema_extra={"example": 1}, description="Assigned Room ID")

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    class Config:
        from_attributes = True
