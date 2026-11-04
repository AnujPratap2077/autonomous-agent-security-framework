
from agent_security.simulator import AgentSimulator
from agent_security.collectors.monitor import EventMonitor
from agent_security.detectors.rule_engine import RuleBasedDetector


def test_normal_agent_pipeline():
    simulator = AgentSimulator()
    monitor = EventMonitor()
    detector = RuleBasedDetector(max_requests=2)

    events = simulator.generate_normal_events()
    monitor.collect_events(events)

    collected_events = monitor.get_events()
    anomalies = detector.detect(collected_events)

    assert len(collected_events) == 3
    assert monitor.get_summary()["successful_events"] == 3
    assert anomalies == []


def test_suspicious_agent_pipeline():
    simulator = AgentSimulator()
    monitor = EventMonitor()
    detector = RuleBasedDetector(max_requests=2)

    events = simulator.generate_suspicious_events()
    monitor.collect_events(events)

    collected_events = monitor.get_events()
    anomalies = detector.detect(collected_events)

    anomaly_types = [anomaly["type"] for anomaly in anomalies]

    assert len(collected_events) == 5
    assert "excessive_requests" in anomaly_types
    assert "restricted_access" in anomaly_types
