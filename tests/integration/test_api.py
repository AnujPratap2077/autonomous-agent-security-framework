
import pytest
from fastapi.testclient import TestClient

from agent_security.api.main import app, monitor


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_monitor():
    """Keep API tests independent by clearing stored events."""
    monitor.events.clear()
    yield
    monitor.events.clear()


def create_event(
    action="file_read",
    status="success",
    agent_id="test-agent-001",
    session_id="test-session-001"
):
    return {
        "agent_id": agent_id,
        "session_id": session_id,
        "action": action,
        "tool_name": "test-tool",
        "status": status,
        "duration_ms": 100
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_receive_single_event():
    response = client.post(
        "/events",
        json=create_event()
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Event received successfully."
    assert response.json()["total_events"] == 1


def test_receive_event_batch():
    events = [
        create_event(action="file_read"),
        create_event(action="web_search"),
    ]

    response = client.post("/events/batch", json=events)

    assert response.status_code == 200
    assert response.json()["events_received"] == 2
    assert response.json()["total_events"] == 2


def test_get_events():
    client.post("/events", json=create_event())

    response = client.get("/events")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_summary():
    events = [
        create_event(status="success"),
        create_event(status="failure"),
        create_event(status="blocked"),
    ]

    client.post("/events/batch", json=events)

    response = client.get("/summary")
    data = response.json()

    assert response.status_code == 200
    assert data["total_events"] == 3
    assert data["successful_events"] == 1
    assert data["failed_events"] == 1
    assert data["blocked_events"] == 1


def test_analyze_suspicious_session():
    events = [
        create_event(action="api_request"),
        create_event(action="api_request"),
        create_event(action="api_request"),
        create_event(
            action="restricted_file_access",
            status="blocked"
        ),
    ]

    client.post("/events/batch", json=events)

    response = client.get(
        "/analyze",
        params={
            "agent_id": "test-agent-001",
            "session_id": "test-session-001"
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["total_events"] == 4
    assert data["risk_assessment"]["risk_score"] == 80
    assert data["risk_assessment"]["risk_level"] == "Critical"
    assert data["risk_assessment"]["total_anomalies"] == 2


def test_analyze_missing_session():
    response = client.get(
        "/analyze",
        params={
            "agent_id": "unknown-agent",
            "session_id": "unknown-session"
        }
    )

    assert response.status_code == 404


def test_empty_batch_rejected():
    response = client.post("/events/batch", json=[])

    assert response.status_code == 400
