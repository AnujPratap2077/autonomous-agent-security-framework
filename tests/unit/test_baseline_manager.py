from agent_security.baselines.manager import AgentBaselineManager
from agent_security.events import AgentEvent


def create_event(agent_id, session_id, count=1):
    return [
        AgentEvent(
            agent_id=agent_id,
            session_id=session_id,
            action="api_request",
            status="success"
        )
        for _ in range(count)
    ]


def test_builds_baseline_from_five_historical_sessions():
    events = []

    for i in range(5):
        events.extend(
            create_event("agent-1", f"session-{i}")
        )

    manager = AgentBaselineManager()
    baseline = manager.build_baseline(events, "agent-1")

    assert baseline is not None
    assert baseline["sessions_used"] == 5
    assert baseline["features"]["api_requests"]["mean"] == 1


def test_ignores_other_agents():
    events = []

    for i in range(5):
        events.extend(
            create_event("agent-1", f"session-{i}")
        )
        events.extend(
            create_event("agent-2", f"session-{i}", count=10)
        )

    manager = AgentBaselineManager()
    baseline = manager.build_baseline(events, "agent-1")

    assert baseline["sessions_used"] == 5
    assert baseline["features"]["total_actions"]["mean"] == 1


def test_excludes_current_session():
    events = []

    for i in range(5):
        events.extend(
            create_event("agent-1", f"session-{i}")
        )

    # Current session contains 10 events and must not affect history.
    events.extend(
        create_event("agent-1", "current-session", count=10)
    )

    manager = AgentBaselineManager()

    baseline = manager.build_baseline(
        events,
        "agent-1",
        exclude_session_id="current-session"
    )

    assert baseline["sessions_used"] == 5
    assert baseline["features"]["total_actions"]["mean"] == 1


def test_returns_none_with_insufficient_history():
    events = []

    for i in range(4):
        events.extend(
            create_event("agent-1", f"session-{i}")
        )

    manager = AgentBaselineManager()
    baseline = manager.build_baseline(events, "agent-1")

    assert baseline is None