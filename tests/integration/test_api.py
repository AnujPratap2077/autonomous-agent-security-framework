
import pytest
from fastapi.testclient import TestClient

from agent_security.api import main as api_main
from agent_security.api.main import app, monitor
from agent_security.database import EventDatabase


TEST_API_KEY = "test-agent-sentinel-key"

client = TestClient(
    app,
    headers={"X-API-Key": TEST_API_KEY}
)


@pytest.fixture(autouse=True)
def clear_monitor(monkeypatch):
    """Give each API test an isolated database and test API key."""

    original_database = monitor.database

    test_database = EventDatabase()
    monitor.database = test_database

    # Use a predictable key during automated tests.
    monkeypatch.setattr(api_main, "API_KEY", TEST_API_KEY)

    yield

    test_database.close()
    monitor.database = original_database


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


# --------------------------------------------------
# AUTHENTICATION TESTS
# --------------------------------------------------

def test_health_endpoint_is_public():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_protected_endpoint_rejects_missing_api_key():
    unauthenticated_client = TestClient(app)

    response = unauthenticated_client.get("/events")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key."


def test_protected_endpoint_rejects_invalid_api_key():
    unauthorized_client = TestClient(
        app,
        headers={"X-API-Key": "incorrect-key"}
    )

    response = unauthorized_client.get("/events")

    assert response.status_code == 401


def test_protected_endpoint_accepts_valid_api_key():
    response = client.get("/events")

    assert response.status_code == 200


# --------------------------------------------------
# EVENT API TESTS
# --------------------------------------------------

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


# --------------------------------------------------
# ANOMALY ANALYSIS TESTS
# --------------------------------------------------

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


def test_behavioural_analysis_uses_historical_sessions():
    agent_id = "behaviour-agent"

    events = []

    for i in range(5):
        events.append(
            create_event(
                agent_id=agent_id,
                session_id=f"history-{i}",
                action="file_read"
            )
        )

    for _ in range(5):
        events.append(
            create_event(
                agent_id=agent_id,
                session_id="current-session",
                action="file_read"
            )
        )

    client.post("/events/batch", json=events)

    response = client.get(
        "/analyze",
        params={
            "agent_id": agent_id,
            "session_id": "current-session"
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["baseline_analysis"]["status"] == "available"
    assert data["baseline_analysis"]["sessions_used"] == 5
    assert len(data["behavioural_anomalies"]) >= 1

    anomaly_types = [
        anomaly["type"]
        for anomaly in data["behavioural_anomalies"]
    ]

    assert "behavioural_deviation" in anomaly_types


def test_rule_detection_works_without_historical_baseline():
    agent_id = "new-agent"

    events = [
        create_event(
            agent_id=agent_id,
            session_id="new-session",
            action="api_request"
        )
        for _ in range(3)
    ]

    client.post("/events/batch", json=events)

    response = client.get(
        "/analyze",
        params={
            "agent_id": agent_id,
            "session_id": "new-session"
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["baseline_analysis"]["status"] == "unavailable"
    assert data["behavioural_anomalies"] == []

    anomaly_types = [
        anomaly["type"]
        for anomaly in data["rule_based_anomalies"]
    ]

    assert "excessive_requests" in anomaly_types
    assert data["risk_assessment"]["risk_score"] == 30


def test_other_agents_history_is_not_used():
    events = []

    for i in range(5):
        events.append(
            create_event(
                agent_id="different-agent",
                session_id=f"history-{i}"
            )
        )

    events.append(
        create_event(
            agent_id="target-agent",
            session_id="current-session"
        )
    )

    client.post("/events/batch", json=events)

    response = client.get(
        "/analyze",
        params={
            "agent_id": "target-agent",
            "session_id": "current-session"
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["baseline_analysis"]["status"] == "unavailable"
    assert data["baseline_analysis"]["sessions_used"] == 0


# --------------------------------------------------
# BATCH SIZE PROTECTION TESTS
# --------------------------------------------------

def test_oversized_batch_rejected():
    events = [
        create_event()
        for _ in range(1001)
    ]

    response = client.post("/events/batch", json=events)

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "Batch cannot contain more than 1000 events."
    )
