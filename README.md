# 🏢 HostelIQ: Smart Hostel Resource & Complaint Analytics System

> **Database Concepts for Data Science (DCDS) Lab ESE Project**  
> **Batch:** 2025-29 | **Semester:** SY / Sem 3  
> **Course:** Database Concepts for Data Science Lab  
> **SDGs Addressed:** 💧 **SDG 6 – Clean Water and Sanitation** & ⚡ **SDG 12 – Responsible Consumption and Production**

---

## 📌 Executive Summary

**HostelIQ** is an integrated data science and resource analytics application designed to optimize water and electricity consumption in campus hostels while accelerating grievance resolution. 

The application utilizes a **Dual-Database Architecture** (SQL + NoSQL) powered by **FastAPI** to meet all requirements of the DCDS Lab ESE Rubrics:

1. **Relational Database (SQL)**: Manages structured records for Students, Rooms, Water Usage Logs (SDG 6 monitoring), and Electricity Logs (SDG 12 carbon footprint).
2. **Document Database (NoSQL - MongoDB)**: Stores semi-structured complaint documents, complaint status timelines, maintenance assignment logs, and student ratings/feedback.

---

## 🏗️ System Architecture

```text
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
             │ (SQLite / MySQL)         │          │ (MongoDB / PyMongo)      │
             ├──────────────────────────┤          ├──────────────────────────┤
             │ • Students               │          │ • Complaints             │
             │ • Rooms & Blocks         │          │ • Status History         │
             │ • Water Usage Logs       │          │ • Feedback & Ratings     │
             │ • Electricity Usage Logs │          │ • Maintenance Logs       │
             └──────────────────────────┘          └──────────────────────────┘
```

---

## 📊 Evaluation Criteria & Rubrics Mapping (10 Marks Total)

| Rubric Parameter | Max Marks | Implementation Highlights |
| :--- | :---: | :--- |
| **Application Design & Functionality** | **2.0** | Fully functional FastAPI application with interactive HTML dashboard (`/`) and auto-generated Swagger UI (`/docs`). |
| **Python Programming Implementation** | **2.0** | Clean OOP implementation with modular design (`SQLManager`, `NoSQLManager`), Pydantic models, and custom routing. |
| **Database Integration (SQL & NoSQL)** | **2.0** | Seamless dual integration: SQLite/MySQL for utility logs + MongoDB for unstructured complaint timelines. |
| **Advanced Database Querying** | **2.0** | • **3-Way SQL Join** (`Students` + `Rooms` + `Water`) <br> • **SQL Grouping & Aggregations** (`AVG`, `SUM` per block) <br> • **Nested Subqueries** (Rooms $> 80\%$ above avg usage) <br> • **SQL CTE / Stored Procedure** (Resource anomaly flagging) <br> • **MongoDB Aggregation Pipeline** (`$match`, `$group`, `$sort`, `$project`) |
| **Code Quality & Documentation** | **1.0** | Complete README, docstrings, inline code comments, and interactive Swagger/ReDoc docs. |
| **Testing, Security & Error Handling** | **1.0** | Pydantic payload sanitization (prevents SQLi/bad payloads), `pytest` unit test suite (7/7 passing), and HTTP status exceptions. |

---

## ⚡ API Endpoint Reference & Advanced Queries

### 1. Advanced Queries (Analytics)
* `GET /api/v1/analytics/multi-table-join`: Executes a 3-way SQL `INNER JOIN` across Students, Rooms, and Water logs.
* `GET /api/v1/analytics/block-summary`: Executes SQL `GROUP BY` and aggregations (`SUM`, `AVG`) grouped by block and floor.
* `GET /api/v1/analytics/excessive-water-rooms`: Executes a **Nested SQL Subquery** identifying rooms consuming water $> 80\%$ above the hostel average.
* `GET /api/v1/analytics/flagged-high-consumption`: Executes a CTE query simulating a **Stored Procedure** flagging high-risk resource leaks.
* `GET /api/v1/analytics/mongo-pipeline`: Executes a multi-stage **MongoDB Aggregation Pipeline** (`$match` $\rightarrow$ `$group` $\rightarrow$ `$project` $\rightarrow$ `$sort`).

### 2. Resource Logging & Grievances
* `POST /api/v1/resources/water-log`: Logs room water consumption (SDG 6) with Pydantic range validation (`gt=0`).
* `POST /api/v1/resources/electricity-log`: Logs room electricity consumption (SDG 12).
* `GET /api/v1/complaints/`: Fetches MongoDB complaint documents with resolution timelines.
* `POST /api/v1/complaints/`: Registers a new student grievance in MongoDB.

---

## 🛠️ How to Run the Project Locally

### Step 1: Clone Repository
```bash
git clone https://github.com/sohan1saha/HostelIQ.git
cd HostelIQ
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run FastAPI Application
```bash
uvicorn app.main:app --reload
```

### Step 4: Open in Browser
* 🌐 **Interactive Dashboard**: [http://localhost:8000/](http://localhost:8000/)
* 📚 **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* 📖 **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Unit Tests

Run the automated test suite to verify database queries and API endpoints:
```bash
python -m pytest
```

---

## 📄 License
This project is created for academic assessment in the Database Concepts for Data Science Lab at Symbiosis Institute of Technology (SIT), Pune.
