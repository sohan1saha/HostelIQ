from fastapi import APIRouter, HTTPException, status, Query, Body
from typing import Optional
from app.models.complaint import ComplaintCreate
from app.database.nosql_manager import nosql_manager
from database_scripts.simulate_maintenance_tickets import simulate_daily_tickets

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

@router.delete("/", summary="Delete All Maintenance Complaints")
def delete_all_complaints():
    """
    Purges all maintenance grievances and complaints from NoSQL document storage.
    """
    try:
        purged = nosql_manager.delete_all_complaints()
        return {
            "status": "success",
            "message": f"Successfully deleted {purged} maintenance complaints",
            "deleted_count": purged
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete complaints: {str(e)}")

@router.get("/sla-metrics", summary="SLA Performance & MTTR Engine")
def get_sla_metrics():
    """
    Reports Mean Time to Resolution (MTTR), SLA compliance rate,
    breached tickets, and active technician dispatch workloads.
    """
    try:
        return nosql_manager.get_sla_and_mttr_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute SLA metrics: {str(e)}")

@router.post("/{complaint_id}/resolve", summary="Resolve Complaint & Record Feedback")
def resolve_complaint_endpoint(
    complaint_id: str,
    rating: int = Query(5, ge=1, le=5, description="Student feedback rating (1-5)"),
    comments: str = Query("Resolved by technician", description="Resolution note")
):
    """
    Marks a ticket as Resolved, records resolution timeline timestamp, and sets feedback.
    """
    try:
        result = nosql_manager.resolve_complaint(complaint_id=complaint_id, rating=rating, comments=comments)
        return {
            "status": "success",
            "message": f"Ticket {complaint_id} resolved successfully",
            "data": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve ticket: {str(e)}")

@router.post("/simulate-tickets", summary="Simulate Daily Maintenance Tickets (Poisson Process)")
def simulate_tickets(date: Optional[str] = Query(default=None, description="Simulation date (YYYY-MM-DD)")):
    """
    Simulates stochastic maintenance tickets based on mathematical queueing theory:
    - Zero-Inflated Poisson arrival rate proportional to occupied room density
    - Volatility factor producing natural variation (Nil, Moderate, Many)
    - Strictly caps ticket generation below occupied room count
    """
    try:
        result = simulate_daily_tickets(target_date=date)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Ticket simulation failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
