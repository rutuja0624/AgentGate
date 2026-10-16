"""Test suite for Mock Engine API endpoints."""

import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.mock_engine import app  # noqa: E402

client = TestClient(app)
AUTH_HEADER = {"X-Internal-Token": os.getenv("ENGINE_INTERNAL_TOKEN", "agentgate_internal_secret_change_in_prod")}


def test_mock_engine_health() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_mock_engine_auth_protection() -> None:
    # Missing token returns 401
    res = client.get("/internal/reviews")
    assert res.status_code == 401

    # Valid token returns 200
    res = client.get("/internal/reviews", headers=AUTH_HEADER)
    assert res.status_code == 200
    assert "items" in res.json()


def test_mock_engine_create_and_get_review() -> None:
    payload = {
        "repo": "agentgate/sample-service",
        "pr_number": 13,
        "head_sha": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1",
        "base_sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
        "mode": "full",
    }
    create_res = client.post("/internal/reviews", json=payload, headers=AUTH_HEADER)
    assert create_res.status_code == 202
    data = create_res.json()
    assert "review_id" in data
    assert data["status"] == "queued"

    review_id = data["review_id"]
    get_res = client.get(f"/internal/reviews/{review_id}", headers=AUTH_HEADER)
    assert get_res.status_code == 200
    review_detail = get_res.json()
    assert review_detail["verdict"] == "BLOCK"
    assert review_detail["risk_score"] == 88


def test_mock_engine_analyze_diff() -> None:
    diff_payload = {
        "diff": "--- a/app.py\n+++ b/app.py\n@@ -1 +1 @@\n-x = 1\n+query = 'SELECT * FROM users WHERE id = %s' % uid",
        "mode": "llm_static",
    }
    res = client.post("/internal/analyze-diff", json=diff_payload, headers=AUTH_HEADER)
    assert res.status_code == 200
    assert res.json()["verdict"] == "BLOCK"
