from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True

def test_setup():
    response = client.get("/api/setup")
    assert response.status_code == 200
    data = response.json()
    assert "demo_mode" in data
    assert "real_mode_preflight" in data

def test_preflight():
    response = client.get("/api/preflight/real-mode")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "gpu" in data

def test_create_and_rename_project():
    response = client.post("/api/projects", data={
        "name": "Test Project",
        "source_type": "photos",
        "preset": "fast",
        "capture_mode": "object"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"

    project_id = data["id"]
    response = client.patch(f"/api/projects/{project_id}", data={"name": "Renamed Project"})
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed Project"
