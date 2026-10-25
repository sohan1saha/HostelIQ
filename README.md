---
title: HostelIQ
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# HostelIQ: Smart Hostel Resource & Complaint Analytics System

> **Database Concepts for Data Science (DCDS) Lab ESE Project**  
> **Batch:** 2025-29 | **Semester:** SY / Sem 3  
> **Course:** Database Concepts for Data Science Lab  
> **SDGs Addressed:** SDG 6 (Clean Water and Sanitation) & SDG 12 (Responsible Consumption and Production)

---

## Executive Summary

HostelIQ is an integrated data science and resource analytics application designed to optimize water and electricity consumption in campus residential facilities while accelerating grievance resolution and facility maintenance. 

The application utilizes a **Dual-Database Architecture** (Relational SQL + Document NoSQL) powered by **FastAPI** to meet all requirements of the DCDS Lab ESE Rubrics:

1. **Relational Database (SQL)**: Manages structured entities including Student profiles, Room allocations across Blocks A-D, Daywise Water Usage Telemetry (SDG 6), Daywise Electricity Logs (SDG 12), and Maintenance Technician Rosters.
2. **Document Database (NoSQL - MongoDB / Resilient JSON Store)**: Stores semi-structured complaint tickets, state machine status timelines, technician auto-assignment metadata, SLA tracking logs, and resident feedback ratings.

---

## Repository File Index & Directory Reference

Below is the directory map and file index for the entire HostelIQ repository. Each file is categorized by architectural layer with explicit descriptions and usage instructions.

| File Path | Component Layer | Primary Purpose | How to Access / Run |
| :--- | :--- | :--- | :--- |
| `app/main.py` | Application Core | FastAPI entry point, CORS middleware, API router mounting, static asset serving, and Jinja2 frontend template rendering. | `uvicorn app.main:app --reload` |
| `app/config.py` | Configuration | Environment configuration and database connection parameters (`DATABASE_URL`, `MONGO_URI`, `PORT`, `ENVIRONMENT`). | Imported by database managers and main application. |
| `app/database/sql_manager.py` | Relational Storage | SQLite/MySQL database interface handling 3-way joins, aggregations, subqueries, EWMA demand forecasting, floor heatmap data, eco-ratings, and room transfers. | Utilized across API routers; initialized on startup. |
| `app/database/nosql_manager.py` | Document Storage | PyMongo/NoSQL JSON manager handling complaint ticketing, trade-based automated technician dispatch, MTTR metrics, SLA enforcement, and feedback. | Utilized across complaint API routes; resilient local fallback. |
| `app/models/student.py` | Data Contracts | Pydantic data validation models for Student registration, profile updates, and room allocations. | Imported by student routers for input/output sanitization. |
| `app/models/resource.py` | Data Contracts | Pydantic validation schemas for Water telemetry (SDG 6) and Electricity consumption logs (SDG 12). | Validates request payloads on resource telemetry endpoints. |
| `app/models/complaint.py` | Data Contracts | Pydantic models for grievance submission, status transitions, SLA target metrics, and student feedback ratings. | Validates complaint submission and status mutation payloads. |
| `app/routers/resources.py` | API Router | REST endpoints for room occupancy lookups, student directory management, room transfers, and utility telemetry ingestion. | Base prefix: `/api/v1/resources` |
| `app/routers/complaints.py` | API Router | REST endpoints for registering grievances, updating ticket status, tracking SLA performance, MTTR, and resolving tickets. | Base prefix: `/api/v1/complaints` |
| `app/routers/analytics.py` | API Router | REST endpoints for multi-table joins, subqueries, floor heatmap data, EWMA predictive forecasting, eco-scorecards, and CSV exports. | Base prefix: `/api/v1/analytics` |
| `app/templates/index.html` | Presentation Layer | Enterprise dashboard frontend with Tailwind CSS, Chart.js telemetry graphs, 2D interactive floor heatmap, and modal wizards. | Rendered at `http://localhost:8000/` |
| `app/static/img/` | UI Assets | Vector branding assets, neon badge logos, and system icons rendered across the navigation header and dashboard cards. | Static mount: `/static/img` |
| `database_scripts/schema.sql` | Database DDL | Relational database schema definition: tables (`rooms`, `students`, `water_consumption`, `electricity_consumption`, `maintenance_staff`), indexes, and triggers. | Loaded during database initialization or reset. |
| `database_scripts/seed_data.sql` | Seed Fixtures | Initial static seed dataset providing baseline rooms, technician staff, and initial utility readings. | Loaded by initialization scripts. |
| `database_scripts/seed_db.py` | Database Seeding | Automated script executing schema creation and baseline fixture insertion into the SQLite database. | `python database_scripts/seed_db.py` |
| `database_scripts/populate_full_hostel.py` | Data Generation | Realistic data populator creating 600 rooms across Blocks A-D, enrolled students, and historical consumption telemetry. | `python database_scripts/populate_full_hostel.py` |
| `database_scripts/simulate_maintenance_tickets.py` | Ticket Generator | Probabilistic ticket generator creating grievances with category trade-matching, priority weights, and technician assignment. | `python database_scripts/simulate_maintenance_tickets.py` |
| `database_scripts/check_db.py` | Diagnostic Tool | Database verification script printing table counts, room occupancies, and consumption aggregate stats. | `python database_scripts/check_db.py` |
| `database_scripts/reset_db.py` | Database Reset | Safe teardown and rebuild utility re-instantiating the schema and baseline data. | `python database_scripts/reset_db.py` |
| `add_students.py` | Interactive CLI | Interactive console tool prompting for target student count (1 to 1,800), auto-populating occupied rooms with telemetry. | `python add_students.py` |
| `add_students.bat` | Windows Launcher | One-click Windows batch launcher wrapping `add_students.py`. | Double-click `add_students.bat` |
| `simulate_tickets.py` | Interactive CLI | Console tool prompting for ticket count or auto-calculating optimal grievance numbers based on occupancy. | `python simulate_tickets.py` |
| `simulate_tickets.bat` | Windows Launcher | One-click Windows batch launcher wrapping `simulate_tickets.py`. | Double-click `simulate_tickets.bat` |
| `delete_all_records.py` | Administrative CLI | Complete wipe script deleting students, utility logs, and complaint documents with room capacity reset. | `python delete_all_records.py` |
| `delete_all_records.bat` | Windows Launcher | One-click Windows batch launcher wrapping `delete_all_records.py`. | Double-click `delete_all_records.bat` |
| `iot_simulator.py` | Telemetry Engine | Simulated IoT sensor script streaming real-time water and electricity pulses to occupied rooms. | `python iot_simulator.py` |
| `tests/test_app.py` | Verification Suite | Automated pytest suite with 19 comprehensive unit tests verifying API contracts, joins, subqueries, transfers, and forecasts. | `python -m pytest` |
| `requirements.txt` | Package Manifest | Declares project dependencies: FastAPI, Uvicorn, SQLite3, PyMongo, Pydantic, Faker, Pytest. | `pip install -r requirements.txt` |
| `README.md` | Documentation | Primary system documentation, architecture blueprints, rubric mapping, and usage guides. | View on GitHub or local markdown viewer. |
| `HostelIQ_Project_Guide.md` | Academic Guide | Complete lab report and submission guide detailing SQL queries, MongoDB pipelines, and DCDS viva answers. | Reference document for presentation and defense. |

---

## System Architecture

```text
                            +---------------------------------+
                            |    Interactive Client / UI      |
                            |  (Tailwind CSS / HTML / JS)     |
                            +----------------+----------------+
                                             | HTTP Requests / JSON
                                             v
                            +---------------------------------+
                            |      FastAPI Backend Engine     |
                            | (main.py + Pydantic + Routers)  |
                            +---------+--------------+--------+
                                      |              |
             +------------------------+-+          +-+------------------------+
             | SQL Database Manager     |          | NoSQL Database Manager   |
             | (SQLite / MySQL)         |          | (MongoDB / Resilient)    |
             +--------------------------+          +--------------------------+
             | - Students               |          | - Complaints Documents   |
             | - Rooms & Blocks (600)   |          | - Status Audit History   |
             | - Water Usage Logs       |          | - SLA Tracking & MTTR    |
             | - Electricity Usage Logs |          | - Staff Dispatch Logs    |
             | - Maintenance Staff      |          | - Feedback & Ratings     |
             +--------------------------+          +--------------------------+
```

---

## Core Enterprise Features

### 1. Interactive 2D Hostel Floor Heatmap
* Visual floor grid spanning Blocks A, B, C, and D across Floors 1, 2, and 3.
* Rooms dynamically color-coded:
  * **Green (Optimal)**: Normal utility consumption.
  * **Amber (Elevated)**: Moderate consumption above baseline.
  * **Red (Leak/Surge)**: High water leak or power spike detected.
  * **Grey (Vacant)**: Zero occupancy room.
* Room click modal reveals live student occupants, today's water and power metrics, and open maintenance tickets.
* Endpoint: `GET /api/v1/analytics/floor-heatmap`

### 2. 7-Day Predictive Demand Forecasting (EWMA)
* Implements Holt-Winters Exponential Weighted Moving Average (EWMA) with level ($\alpha = 0.35$) and trend ($\beta = 0.15$) smoothing.
* Projects the upcoming 7 days of campus-wide water consumption (Liters) and electricity demand (kWh).
* Dual-axis visualization in the dashboard powered by Chart.js.
* Endpoint: `GET /api/v1/analytics/forecast`

### 3. Automated Staff Dispatch & SLA Engine
* Automatically routes new maintenance tickets to the least-loaded technician specializing in the required trade:
  * Plumbing issues $\rightarrow$ SDG 6 Water Technicians
  * Electrical issues $\rightarrow$ SDG 12 Electrical Technicians
  * Sanitation and Structural issues $\rightarrow$ Sanitation/General Technicians
* Enforces target resolution SLAs based on urgency:
  * High / Critical: 4 hours
  * Medium: 12 hours
  * Low: 24 hours
* Calculates live Mean Time to Resolution (MTTR) across resolved grievances.
* Endpoints: `GET /api/v1/complaints/sla-metrics`, `POST /api/v1/complaints/{id}/resolve`

### 4. Carbon Footprint & Eco-Rating Scorecard
* Quantifies campus environmental impact:
  * Electricity converted to estimated emissions using the regional grid factor ($0.82 \text{ kg CO}_2\text{e/kWh}$).
  * Quantifies water leak prevention savings in volumetric and financial metrics.
* Assigns an Eco-Rating (A+, A, B, C, D, F) to each Block and Floor based on per-capita daily conservation.
* Endpoint: `GET /api/v1/analytics/eco-scorecard`

### 5. Student Room Transfer Wizard
* Enables administrative student relocation between rooms.
* Performs instant transactional validation ensuring the destination room does not exceed the strict 3-bed capacity limit.
* Endpoint: `POST /api/v1/resources/students/transfer`

### 6. One-Click Audit Reports (CSV Export)
* Direct downloadable CSV spreadsheets formatted for institutional auditing:
  * Daywise telemetry audit logs across all occupied rooms.
  * Active resident and room allocation directory.
  * Maintenance grievance logs with technician dispatch and SLA status.
* Endpoints:
  * `GET /api/v1/analytics/export/daywise-telemetry`
  * `GET /api/v1/analytics/export/residents`
  * `GET /api/v1/analytics/export/grievances`

---

## Evaluation Criteria & Rubrics Mapping (10 Marks Total)

| Rubric Parameter | Max Marks | Implementation Highlights |
| :--- | :---: | :--- |
| **Application Design & Functionality** | **2.0** | Full-stack FastAPI application with interactive dashboard (`/`), responsive 2D floor heatmap, CSV reporting, and Swagger documentation (`/docs`). |
| **Python Programming Implementation** | **2.0** | Modular architecture with strict OOP patterns (`SQLManager`, `NoSQLManager`), Pydantic v2 validation models, and isolated router modules. |
| **Database Integration (SQL & NoSQL)** | **2.0** | Dual integration: Relational SQLite/MySQL for telemetry and capacity management + MongoDB / resilient document store for lifecycle complaints. |
| **Advanced Database Querying** | **2.0** | 3-way SQL joins, multi-table aggregations (`GROUP BY`, `HAVING`), nested subqueries (excessive consumption detection), and MongoDB aggregation pipelines. |
| **Code Quality & Documentation** | **1.0** | Comprehensive README file index, clean docstrings, clear module boundaries, and zero syntax or type warnings. |
| **Testing, Security & Error Handling** | **1.0** | 19 automated unit tests passing via `pytest`, Pydantic payload sanitation, capacity-boundary checks, and HTTP error responses. |

---

## API Endpoint Reference

### Analytics & Advanced Database Queries
* `GET /api/v1/analytics/multi-table-join`: Executes a 3-way SQL `INNER JOIN` across Students, Rooms, and Water consumption logs.
* `GET /api/v1/analytics/block-summary`: Executes SQL `GROUP BY` and aggregations (`SUM`, `AVG`) grouped by block and floor.
* `GET /api/v1/analytics/excessive-water-rooms`: Executes a nested SQL subquery identifying rooms consuming $> 80\%$ above the hostel average.
* `GET /api/v1/analytics/flagged-high-consumption`: Executes a Common Table Expression (CTE) query flagging resource anomalies.
* `GET /api/v1/analytics/mongo-pipeline`: Executes a multi-stage MongoDB aggregation pipeline (`$match` $\rightarrow$ `$group` $\rightarrow$ `$project` $\rightarrow$ `$sort`).
* `GET /api/v1/analytics/floor-heatmap`: Returns block-by-block room status, consumption, and ticket counts for the 2D floor visualizer.
* `GET /api/v1/analytics/forecast`: Computes 7-day projected water and electricity demand using EWMA forecasting.
* `GET /api/v1/analytics/eco-scorecard`: Computes carbon emissions, water leak cost savings, and per-block eco letter grades.
* `GET /api/v1/analytics/export/daywise-telemetry`: Generates downloadable CSV of daywise utility consumption.
* `GET /api/v1/analytics/export/residents`: Generates downloadable CSV resident roster.
* `GET /api/v1/analytics/export/grievances`: Generates downloadable CSV maintenance ticket history.

### Resource Management
* `GET /api/v1/resources/occupancy`: Returns hostel-wide room and bed capacity metrics.
* `GET /api/v1/resources/students`: Returns resident directory with room details.
* `POST /api/v1/resources/students/transfer`: Atomically transfers a student to a destination room with capacity validation.
* `POST /api/v1/resources/water-log`: Logs room water consumption (SDG 6) with range validation (`gt=0`).
* `POST /api/v1/resources/electricity-log`: Logs room electricity consumption (SDG 12).
* `DELETE /api/v1/resources/reset-all`: Clears utility logs, students, and complaint documents.

### Grievances & Maintenance Ticketing
* `GET /api/v1/complaints/`: Fetches complaint documents with resolution history and assigned staff.
* `POST /api/v1/complaints/`: Registers a grievance and triggers automated trade-based technician dispatch.
* `POST /api/v1/complaints/{complaint_id}/resolve`: Resolves a complaint, captures resident feedback, and logs MTTR duration.
* `GET /api/v1/complaints/sla-metrics`: Returns live SLA compliance rates and average MTTR metrics.

---

## How to Run the Project Locally

### 1. Clone the Repository
```bash
git clone https://github.com/sohan1saha/HostelIQ.git
cd HostelIQ
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
```bash
python database_scripts/seed_db.py
```

### 4. Run the FastAPI Application
```bash
uvicorn app.main:app --reload
```

### 5. Access Interfaces
* **Interactive Dashboard**: [http://localhost:8000/](http://localhost:8000/)
* **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Interactive Simulation Tools

The repository includes ready-to-run batch files and Python scripts for operational workflows:

* **Populate Students & Telemetry**:
  ```bash
  python add_students.py
  # Or double-click add_students.bat
  ```
  Prompts for student count (1 to 1,800), populates 3-bed capacity rooms, and auto-syncs utility consumption for occupied rooms.

* **Simulate Maintenance Tickets**:
  ```bash
  python simulate_tickets.py
  # Or double-click simulate_tickets.bat
  ```
  Generates grievances with automated technician assignment and SLA deadlines.

* **Clear All Records**:
  ```bash
  python delete_all_records.py
  # Or double-click delete_all_records.bat
  ```
  Clears students, telemetry logs, and complaints while preserving the physical room catalog.

---

## Running Automated Tests

Run the test suite to verify database queries, API endpoints, capacity constraints, and forecasting calculations:

```bash
python -m pytest
```

Expected output:
```text
======================== 19 passed in 5.12s ========================
```

---

## License & Academic Disclaimer

This project is developed for academic assessment in the Database Concepts for Data Science Lab at Symbiosis Institute of Technology (SIT), Pune.
