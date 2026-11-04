import pytest
from pydantic import ValidationError

from agent_security.events import AgentEvent


def test_create_valid_agent_event():
    event = AgentEvent(
        agent_id="agent-001",
        session_id="session-001",
        action="file_read",
        tool_name="file_reader",
        status="success",
        duration_ms=120.5,
    )

    assert event.agent_id == "agent-001"
    assert event.session_id == "session-001"
    assert event.action == "file_read"
    assert event.tool_name == "file_reader"
    assert event.status == "success"
    assert event.duration_ms == 120.5


def test_event_generates_unique_ids():
    event1 = AgentEvent(
        agent_id="agent-001",
        session_id="session-001",
        action="file_read",
        status="success",
    )

    event2 = AgentEvent(
        agent_id="agent-001",
        session_id="session-001",
        action="file_read",
        status="success",
    )

    assert event1.event_id != event2.event_id


def test_event_rejects_negative_duration():
    with pytest.raises(ValidationError):
        AgentEvent(
            agent_id="agent-001",
            session_id="session-001",
            action="file_read",
            status="success",
            duration_ms=-10,
        )


def test_event_rejects_invalid_status():
    with pytest.raises(ValidationError):
        AgentEvent(
            agent_id="agent-001",
            session_id="session-001",
            action="file_read",
            status="unknown",
        )


def test_event_can_be_serialized_to_json():
    event = AgentEvent(
        agent_id="agent-001",
        session_id="session-001",
        action="file_read",
        status="success",
    )

    json_data = event.model_dump_json()

    assert '"agent_id":"agent-001"' in json_data
    assert '"status":"success"' in json_data


def test_event_contains_utc_timestamp():
    event = AgentEvent(
        agent_id="agent-001",
        session_id="session-001",
        action="file_read",
        status="success",
    )

    assert event.timestamp.tzinfo is not None
    assert event.timestamp.utcoffset().total_seconds() == 0