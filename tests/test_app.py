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
    assert len(data["data"]) > 0

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
    # Negative water liters should fail Pydantic validation (gt=0)
    invalid_payload = {
        "room_id": 1,
        "log_date": "2026-10-06",
        "water_used_liters": -50.0,
        "leak_flag": 0
    }
    response = client.post("/api/v1/resources/water-log", json=invalid_payload)
    assert response.status_code == 422  # Unprocessable Entity
