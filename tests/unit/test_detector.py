
from agent_security.detectors.rule_engine import RuleBasedDetector
from agent_security.simulator import AgentSimulator


def test_detects_restricted_access():
    simulator = AgentSimulator()
    detector = RuleBasedDetector()

    events = simulator.generate_suspicious_events()
    anomalies = detector.detect(events)

    assert any(
        anomaly["type"] == "restricted_access"
        for anomaly in anomalies
    )


def test_detects_excessive_requests():
    simulator = AgentSimulator()
    detector = RuleBasedDetector(max_requests=2)

    events = simulator.generate_suspicious_events()
    anomalies = detector.detect(events)

    assert any(
        anomaly["type"] == "excessive_requests"
        for anomaly in anomalies
    )


def test_normal_events_have_no_anomalies():
    simulator = AgentSimulator()
    detector = RuleBasedDetector()

    events = simulator.generate_normal_events()
    anomalies = detector.detect(events)

    assert anomalies == []


def test_detector_returns_empty_list_for_no_events():
    detector = RuleBasedDetector()

    anomalies = detector.detect([])

    assert anomalies == []
