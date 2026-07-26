"""
Pytest integration tests for LedgerDesk CA FastAPI backend routers.
Run from backend directory: pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "LedgerDesk CA"

def test_auth_login_validation():
    # Login without credentials should fail with 422 validation error
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422

def test_public_routes():
    # Serve landing page
    response = client.get("/")
    assert response.status_code == 200
