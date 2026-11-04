
from agent_security.simulator import AgentSimulator


def test_simulator_generates_normal_events():
    simulator = AgentSimulator()

    events = simulator.generate_normal_events()

    assert len(events) == 3
    assert all(event.status == "success" for event in events)


def test_simulator_generates_suspicious_events():
    simulator = AgentSimulator()

    events = simulator.generate_suspicious_events()

    assert len(events) == 5
    assert any(event.status == "blocked" for event in events)
    assert any(event.status == "failure" for event in events)


def test_simulator_uses_custom_agent_id():
    simulator = AgentSimulator(agent_id="test-agent")

    events = simulator.generate_normal_events()

    assert all(event.agent_id == "test-agent" for event in events)


def test_simulator_events_have_unique_ids():
    simulator = AgentSimulator()

    events = simulator.generate_normal_events()

    event_ids = [event.event_id for event in events]

    assert len(event_ids) == len(set(event_ids))
