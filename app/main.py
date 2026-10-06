from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.config import settings
from app.routers import analytics, resources, complaints

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## HostelIQ: Smart Hostel Resource & Complaint Analytics System
    Developed for Database Concepts for Data Science (DCDS) Lab ESE Project.
    
    ### 🎯 SDG Alignments:
    * **SDG 6 (Clean Water and Sanitation)**: Water flow telemetry, leakage flagging, plumbing grievance tracking.
    * **SDG 12 (Responsible Consumption & Production)**: Electricity usage monitoring, carbon offset metrics, peak hour alerts.

    ### ⚡ Database Architecture:
    * **Relational (SQL)**: Students, Rooms, Water Logs, Electricity Logs (Multi-Table Joins, Subqueries, Aggregations, Stored Procedures).
    * **Non-Relational (NoSQL)**: MongoDB Complaints Collection ($match, $group, $sort, $unwind aggregation pipelines).
    """
)

# Setup Templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Include API Routers
app.include_router(analytics.router)
app.include_router(resources.router)
app.include_router(complaints.router)

@app.get("/", response_class=HTMLResponse, summary="Interactive HostelIQ Dashboard")
def render_dashboard(request: Request):
    """
    Renders the live visual analytics dashboard.
    """
    return templates.TemplateResponse("index.html", {"request": request, "title": settings.PROJECT_NAME})

@app.get("/health", summary="System Health Check")
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
