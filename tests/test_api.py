from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_endpoint_returns_response():
    resp = client.post(
        "/api/chat",
        json={"user_query": "Create a territory plan for Territory T001", "session_id": "session-123", "user_id": "user-456"},
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "ok"
    assert "Territory plan for T001" in payload["response"]
