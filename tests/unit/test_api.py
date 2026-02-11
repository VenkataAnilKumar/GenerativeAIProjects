"""Basic tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_readiness_check():
    """Test readiness check endpoint"""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_liveness_check():
    """Test liveness check endpoint"""
    response = client.get("/api/v1/live")
    assert response.status_code == 200
    assert response.json()["status"] == "live"
