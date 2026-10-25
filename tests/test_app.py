from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "HostelIQ" in response.text

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_multi_table_join_query():
    response = client.get("/api/v1/analytics/multi-table-join")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

def test_sql_aggregation_query():
    response = client.get("/api/v1/analytics/block-summary")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

def test_sql_nested_subquery():
    response = client.get("/api/v1/analytics/excessive-water-rooms")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

def test_mongo_aggregation_pipeline():
    response = client.get("/api/v1/analytics/mongo-pipeline")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

def test_water_log_pydantic_validation_success():
    payload = {
        "room_id": 1,
        "log_date": "2026-10-06",
        "water_used_liters": 150.0,
        "leak_flag": 0
    }
    response = client.post("/api/v1/resources/water-log", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "success"

def test_water_log_pydantic_validation_failure():
    invalid_payload = {
        "room_id": 1,
        "log_date": "2026-10-06",
        "water_used_liters": -50.0,
        "leak_flag": 0
    }
    response = client.post("/api/v1/resources/water-log", json=invalid_payload)
    assert response.status_code == 422

def test_consumption_breakdown_endpoints():
    r1 = client.get("/api/v1/analytics/consumption-breakdown?group_by=room")
    assert r1.status_code == 200
    assert isinstance(r1.json()["items"], list)

    r2 = client.get("/api/v1/analytics/consumption-breakdown?group_by=floor")
    assert r2.status_code == 200
    assert "conjoined_summary" in r2.json()

    r3 = client.get("/api/v1/analytics/consumption-breakdown?group_by=conjoined&rooms=A-101,B-101")
    assert r3.status_code == 200
    summary = r3.json()["conjoined_summary"]
    assert summary["total_rooms"] >= 0
    assert summary["total_water"] >= 0

def test_iot_telemetry_simulation():
    payload = {
        "target_date": "2026-10-25",
        "anomaly_rate": 0.1
    }
    response = client.post("/api/v1/resources/simulate-telemetry", json=payload)
    assert response.status_code in [201, 400]
    if response.status_code == 201:
        data = response.json()
        assert data["status"] == "success"
        assert "rooms_logged" in data
        assert "leaks_detected" in data
        assert "peak_surges_detected" in data

def test_daywise_telemetry_logs():
    response = client.get("/api/v1/resources/daywise-logs?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total_records" in data
    assert isinstance(data["data"], list)

def test_simulate_tickets():
    response = client.post("/api/v1/complaints/simulate-tickets")
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "tickets_created" in data
        assert "occupied_rooms" in data
        assert "classification" in data
        assert "lambda" in data
        if data["occupied_rooms"] > 0:
            assert data["tickets_created"] < data["occupied_rooms"]

def test_delete_all_complaints():
    test_complaint = {
        "student_id": "STU_TEST",
        "student_name": "Test Student",
        "room_number": "A-101",
        "category": "Water Leakage",
        "sdg_target": "SDG 6",
        "description": "Test fixture leak for deletion check",
        "priority": "Low",
        "created_at": "2026-10-25"
    }
    create_resp = client.post("/api/v1/complaints/", json=test_complaint)
    assert create_resp.status_code == 201

    del_resp = client.delete("/api/v1/complaints/")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"

    get_resp = client.get("/api/v1/complaints/")
    assert get_resp.status_code == 200
    assert get_resp.json()["total_complaints"] == 0

def test_floor_heatmap():
    resp = client.get("/api/v1/analytics/floor-heatmap?block=Block-A&floor=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["block"] == "Block-A"
    assert data["floor"] == 1
    assert "rooms" in data
    assert len(data["rooms"]) == 10
    # Every room has status in allowed set
    for r in data["rooms"]:
        assert r["status"] in ["vacant", "optimal", "elevated", "alert"]

def test_resource_forecast():
    resp = client.get("/api/v1/analytics/forecast?days=7")
    assert resp.status_code == 200
    data = resp.json()
    assert "forecast" in data
    assert "summary" in data
    assert "has_data" in data

def test_eco_scorecard():
    resp = client.get("/api/v1/analytics/eco-scorecard")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_co2e_emissions_kg" in data
    assert "water_leaks_prevented" in data
    assert "blocks" in data
    assert len(data["blocks"]) == 10

def test_csv_exports():
    # Test daywise telemetry export
    r1 = client.get("/api/v1/analytics/export/daywise-telemetry")
    assert r1.status_code == 200
    assert "text/csv" in r1.headers["content-type"]
    assert "Room Number" in r1.text

    # Test residents export
    r2 = client.get("/api/v1/analytics/export/residents")
    assert r2.status_code == 200
    assert "text/csv" in r2.headers["content-type"]
    assert "Student ID" in r2.text

    # Test grievances export
    r3 = client.get("/api/v1/analytics/export/grievances")
    assert r3.status_code == 200
    assert "text/csv" in r3.headers["content-type"]
    assert "Ticket ID" in r3.text

def test_sla_metrics_and_resolve():
    # Create complaint to check auto-dispatch and SLA
    test_complaint = {
        "student_id": "STU_DISPATCH",
        "student_name": "Dispatch Test",
        "room_number": "A-102",
        "category": "Plumbing Issue",
        "sdg_target": "SDG 6",
        "description": "Sink tap leaking",
        "priority": "High"
    }
    c_resp = client.post("/api/v1/complaints/", json=test_complaint)
    assert c_resp.status_code == 201
    created_ticket = c_resp.json()["data"]
    assert "assigned_staff_name" in created_ticket
    assert created_ticket["sla_deadline_hours"] == 4

    # Check SLA metrics endpoint
    sla_resp = client.get("/api/v1/complaints/sla-metrics")
    assert sla_resp.status_code == 200
    sla_data = sla_resp.json()
    assert "mttr_hours" in sla_data
    assert "technicians" in sla_data

    # Resolve the ticket
    cid = created_ticket["complaint_id"]
    res_resp = client.post(f"/api/v1/complaints/{cid}/resolve?rating=5&comments=Fixed")
    assert res_resp.status_code == 200
    assert res_resp.json()["data"]["status"] == "Resolved"

def test_student_transfer():
    # Pick student STU20250001
    students_resp = client.get("/api/v1/resources/students")
    assert students_resp.status_code == 200
    students = students_resp.json()["data"]
    if students:
        target_stu = students[0]["student_id"]
        # Find a room that has vacant space (e.g. room_id 590)
        transfer_payload = {
            "student_id": target_stu,
            "target_room_id": 590
        }
        resp = client.post("/api/v1/resources/students/transfer", json=transfer_payload)
        assert resp.status_code in [200, 400]

def test_simulation_batch_populate():
    resp = client.post("/api/v1/resources/batch-populate", json={"count": 50, "auto_sync_telemetry": False})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["registered_students"] == 50
