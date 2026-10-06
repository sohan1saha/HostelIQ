from fastapi import APIRouter, HTTPException, status
from app.models.complaint import ComplaintCreate
from app.database.nosql_manager import nosql_manager

router = APIRouter(prefix="/api/v1/complaints", tags=["NoSQL Complaint Management"])

@router.get("/", summary="Get All Complaints (NoSQL Document Store)")
def get_complaints():
    """
    Retrieves all hostel complaints stored in MongoDB JSON document format.
    """
    try:
        data = nosql_manager.get_all_complaints()
        return {
            "total_complaints": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve complaints: {str(e)}")

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register New Complaint")
def create_complaint(payload: ComplaintCreate):
    """
    Registers a new student grievance in MongoDB with status timeline tracking.
    Validated by Pydantic payload model.
    """
    try:
        complaint_dict = payload.model_dump()
        result = nosql_manager.create_complaint(complaint_dict)
        return {
            "status": "success",
            "message": "Complaint registered successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register complaint: {str(e)}")
