import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

REQUEST_BODY = {
    "user_query": "Create a territory plan for Territory T001 and identify top accounts.",
    "session_id": "session-smoke",
    "user_id": "user-smoke",
}

GET_ROUTES = [
    "/api/health",
    "/api/metrics",
    "/api/sessions/session-smoke",
    "/api/workflows/workflow-smoke",
]

POST_ROUTES = [
    "/api/chat",
    "/api/agent/run",
    "/api/territories/analyze",
    "/api/territories/plan",
    "/api/accounts/prioritize",
    "/api/accounts/analyze",
    "/api/documents/upload",
    "/api/documents/ingest",
    "/api/approval/workflow-smoke",
]


@pytest.mark.parametrize("path", GET_ROUTES)
def test_get_route_returns_200(path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, f"{path} -> {response.status_code}"


@pytest.mark.parametrize("path", POST_ROUTES)
def test_post_route_returns_200(path: str) -> None:
    response = client.post(path, json=REQUEST_BODY)
    assert response.status_code == 200, f"{path} -> {response.status_code}"


def test_metrics_endpoint_returns_live_aggregates() -> None:
    response = client.get("/api/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_territories"] == 3
    assert payload["total_accounts"] == 5
    assert payload["open_opportunities"] == 5
    assert payload["pipeline_value"] > 0
    assert payload["status"] == "ready"


def test_approval_endpoint_reflects_decision() -> None:
    approved = client.post("/api/approval/wf-1", json={"decision": "APPROVED"})
    assert approved.status_code == 200
    assert approved.json() == {"workflow_id": "wf-1", "approval": "APPROVED"}

    rejected = client.post("/api/approval/wf-1", json={"decision": "REJECTED"})
    assert rejected.status_code == 200
    assert rejected.json() == {"workflow_id": "wf-1", "approval": "REJECTED"}


def test_approval_endpoint_defaults_to_pending_without_decision() -> None:
    response = client.post("/api/approval/wf-2")
    assert response.status_code == 200
    assert response.json()["approval"] == "PENDING"
