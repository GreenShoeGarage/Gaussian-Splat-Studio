from fastapi.testclient import TestClient
from app import app
client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["version"] == "1.0.0-mvp"

def test_dependencies():
    r = client.get("/api/dependencies")
    assert r.status_code == 200
    assert "basic_ready" in r.json()

def test_environment():
    r = client.get("/api/environment")
    assert r.status_code == 200
    assert "commands" in r.json()

def test_engines():
    r = client.get("/api/engines")
    assert r.status_code == 200
    assert "engines" in r.json()

def test_create_project():
    r = client.post("/api/projects", data={"name":"Test Project","preset":"fast"})
    assert r.status_code == 200
    assert "engine" in r.json()
