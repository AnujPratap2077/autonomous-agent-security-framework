
from agent_security.collectors.monitor import EventMonitor
from agent_security.simulator import AgentSimulator


def test_monitor_collects_single_event():
    simulator = AgentSimulator()
    monitor = EventMonitor()

    event = simulator.generate_normal_events()[0]
    monitor.collect_event(event)

    assert len(monitor.get_events()) == 1


def test_monitor_collects_multiple_events():
    simulator = AgentSimulator()
    monitor = EventMonitor()

    events = simulator.generate_normal_events()
    monitor.collect_events(events)

    assert len(monitor.get_events()) == 3


def test_monitor_generates_correct_summary():
    simulator = AgentSimulator()
    monitor = EventMonitor()

    normal = simulator.generate_normal_events()
    suspicious = simulator.generate_suspicious_events()

    monitor.collect_events(normal)
    monitor.collect_events(suspicious)

    summary = monitor.get_summary()

    assert summary["total_events"] == 9
    assert summary["successful_events"] == 6
    assert summary["failed_events"] == 2
    assert summary["blocked_events"] == 1


def test_monitor_returns_copy_of_events():
    simulator = AgentSimulator()
    monitor = EventMonitor()

    monitor.collect_events(simulator.generate_normal_events())

    events = monitor.get_events()
    events.clear()

    assert len(monitor.get_events()) == 3
