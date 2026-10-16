"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_endpoint() -> None:
    """Test that /healthz returns 200 with service ok payload."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "agentgate-engine"
    assert "version" in data
