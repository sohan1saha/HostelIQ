# HostelIQ: Smart Hostel Resource & Complaint Analytics System
> **DCDS Lab ESE Project Guide & Blueprint (FastAPI Edition)**  
> **Batch:** 2025-29 | **Semester:** SY / Sem 3 | **Course:** Database Concepts for Data Science Lab  
> **SDG Alignment:** SDG 6 (Clean Water & Sanitation) & SDG 12 (Responsible Consumption & Production)

---

## 💡 Can we use FastAPI? **YES, ABSOLUTELY!**

In fact, using **FastAPI** is an **excellent choice** that will impress evaluators because it directly covers multiple evaluation parameters:

1. **Automatic Documentation & UI (1 Mark)**: FastAPI automatically generates interactive Swagger UI documentation at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`. You can also serve simple HTML/JS dashboard templates or Jinja2 pages.
2. **Testing, Validation & Error Handling (1 Mark)**: FastAPI uses **Pydantic schemas**, which enforce strict data type validation, payload sanitization, and automatic 422 HTTP error responses for bad data out-of-the-box!
3. **Modular Python Programming & OOP (2 Marks)**: Clean separation of routes using `APIRouter`, models, controllers, and database managers (`SQLManager`, `NoSQLManager`).

---

## 📌 Executive Summary & Rubric Alignment (10 Marks Total)

| Evaluation Parameter | Max Marks | Targeted Score | Key FastAPI Deliverables |
| :--- | :---: | :---: | :--- |
| **1. Application Design & Functionality** | 2.0 | 2.0 | FastAPI RESTful service + Interactive Swagger UI (`/docs`) / HTML Analytics Dashboard. |
| **2. Python Programming Implementation** | 2.0 | 2.0 | OOP implementation, `APIRouter` modules, `Pydantic` models, database manager classes. |
| **3. Database Integration (SQL & NoSQL)** | 2.0 | 2.0 | Dual-DB connectivity: SQLAlchemy/MySQL for relational data + PyMongo/Motor for MongoDB. |
| **4. Advanced Database Querying & Retrieval** | 2.0 | 2.0 | REST Endpoints triggering SQL Joins, Subqueries, Stored Procedures & MongoDB Aggregation Pipelines. |
| **5. Code Quality, Documentation & UI** | 1.0 | 1.0 | Auto-generated OpenAPI/Swagger UI, clean docstrings, Pydantic field descriptions. |
| **6. Testing, Validation & Error Handling** | 1.0 | 1.0 | Pydantic data validation, custom HTTP status codes (200, 400, 404, 500), and `HTTPException` handling. |

---

## 🏗️ System Architecture (FastAPI + SQL + NoSQL)

```
                            ┌─────────────────────────────────┐
                            │    Interactive Client / UI      │
                            │  (Swagger UI / HTML Dashboard)  │
                            └────────────────┬────────────────┘
                                             │ HTTP Requests / JSON
                                             ▼
                            ┌─────────────────────────────────┐
                            │      FastAPI Backend Engine     │
                            │ (main.py + Pydantic + Routers)  │
                            └─────────┬──────────────┬────────┘
                                      │              │
             ┌────────────────────────┴─┐          ┌─┴────────────────────────┐
             │ SQL Database Manager     │          │ NoSQL Database Manager   │
             │ (SQLAlchemy / MySQL)     │          │ (PyMongo / MongoDB)      │
             ├──────────────────────────┤          ├──────────────────────────┤
             │ • Students               │          │ • Complaints             │
             │ • Rooms & Blocks         │          │ • Status History         │
             │ • Water Usage Logs       │          │ • Feedback & Ratings     │
             │ • Electricity Usage Logs │          │ • Telemetry Logs         │
             └──────────────────────────┘          └──────────────────────────┘
```

---

## 📊 Database Design Breakdown

### 1. SQL Schema (Relational Data & Utility Monitoring)
* `Students` (`student_id` PK, `name`, `email`, `room_id` FK, `block`)
* `Rooms` (`room_id` PK, `block`, `floor`, `room_number`, `capacity`)
* `Water_Consumption` (`log_id` PK, `room_id` FK, `log_date`, `water_used_liters`, `leak_flag`)
* `Electricity_Consumption` (`log_id` PK, `room_id` FK, `log_date`, `kwh_consumed`, `peak_usage_flag`)
* `Maintenance_Staff` (`staff_id` PK, `name`, `specialization`, `contact_no`)

### 2. NoSQL Schema (MongoDB JSON Documents)
* Collection: `complaints`
```json
{
  "_id": "ObjectId(...)",
  "complaint_id": "CMP1001",
  "student_id": "STU2025001",
  "room_number": "B-304",
  "category": "Water Leakage",
  "sdg_target": "SDG 6",
  "description": "Pipe leaking under the sink causing water overflow.",
  "priority": "High",
  "status": "In Progress",
  "assigned_staff_id": 102,
  "timeline": [
    { "status": "Submitted", "timestamp": "2026-10-01T09:00:00Z" }
  ],
  "feedback": { "rating": 5, "comments": "Quick fix!" }
}
```

---

## ⚡ FastAPI Endpoints & Advanced Query Strategy

| Endpoint | Method | DB Source | Purpose & Advanced Query Used |
| :--- | :---: | :---: | :--- |
| `/api/v1/analytics/high-water-usage` | `GET` | SQL | Multi-Table Join & Subquery (Rooms consuming > 80% above average). |
| `/api/v1/analytics/electricity-summary` | `GET` | SQL | Grouping & Aggregations (`AVG`, `SUM` per block/floor). |
| `/api/v1/reports/flagged-rooms` | `POST` | SQL | Executes SQL **Stored Procedure** `FlagHighResourceConsumingRooms(threshold)`. |
| `/api/v1/complaints/analytics` | `GET` | NoSQL | **MongoDB Aggregation Pipeline** (`$match`, `$group`, `$sort` rating & categories). |
| `/api/v1/complaints` | `POST` | NoSQL | Creates a complaint with Pydantic payload validation & initial timeline push. |

---

## 💻 FastAPI Project Directory Structure

```text
HostelIQ/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI Application Entrypoint
│   ├── config.py                # Database URLs & Environment settings
│   │
│   ├── models/                  # Pydantic Request/Response Models (Validation)
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── resource.py
│   │   └── complaint.py
│   │
│   ├── database/                # Database Managers
│   │   ├── __init__.py
│   │   ├── sql_db.py            # MySQL/SQLAlchemy Connection & Queries (Joins, Stored Proc)
│   │   └── mongo_db.py          # PyMongo Connection & Aggregation Pipelines
│   │
│   ├── routers/                 # API Endpoint Controllers (Modular Routing)
│   │   ├── __init__.py
│   │   ├── analytics.py         # SQL & NoSQL Analytics Endpoints
│   │   ├── complaints.py        # MongoDB Complaint CRUD & Aggregations
│   │   └── resources.py        # SQL Resource Monitoring Endpoints
│   │
│   └── static/                  # Optional HTML/JS frontend dashboard
│       └── index.html
│
├── schema.sql                   # SQL Schema Creation Script
├── requirements.txt             # Dependencies (fastapi, uvicorn, pymongo, sqlalchemy, mysql-connector-python, pydantic)
├── README.md                    # How to run FastAPI app
└── HostelIQ_Project_Guide.md   # This Guide Document
```

---

## 🛠️ Step-by-Step Implementation Plan for FastAPI

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn pymongo sqlalchemy mysql-connector-python pydantic
```

### Step 2: Run FastAPI App
```bash
uvicorn app.main:app --reload
```
Access the interactive docs at: `http://localhost:8000/docs`

---

## 🎯 Verification Checklist for 10/10 Marks with FastAPI

- [x] **Application Design & Functionality**: RESTful API design with Swagger UI / HTML dashboard.
- [x] **Python Implementation**: FastAPI + Pydantic + Modular `APIRouter` structure.
- [x] **Database Integration**: MySQL (relational usage data) + MongoDB (complaints & logs).
- [x] **Advanced Database Querying**: SQL Joins, Grouping, Stored Procedures + MongoDB `$match`/`$group` Aggregations exposed via endpoints.
- [x] **Testing & Validation**: Pydantic models automatically validate student IDs, numeric usage ranges, and email formats; FastAPI raises proper `HTTPException(400/404/500)`.
- [x] **Documentation**: Automatic interactive Swagger docs generated at `/docs`.
