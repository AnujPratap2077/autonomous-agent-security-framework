
from agent_security.simulator import AgentSimulator
from agent_security.collectors.monitor import EventMonitor
from agent_security.detectors.rule_engine import RuleBasedDetector
from agent_security.risk.assessor import RiskAssessor


def test_normal_agent_pipeline():
    simulator = AgentSimulator()
    monitor = EventMonitor()
    detector = RuleBasedDetector(max_requests=2)
    risk_assessor = RiskAssessor()

    events = simulator.generate_normal_events()
    monitor.collect_events(events)

    collected_events = monitor.get_events()
    anomalies = detector.detect(collected_events)
    risk = risk_assessor.assess(anomalies)

    assert len(collected_events) == 3
    assert monitor.get_summary()["successful_events"] == 3
    assert anomalies == []
    assert risk["risk_score"] == 0
    assert risk["risk_level"] == "Low"


def test_suspicious_agent_pipeline():
    simulator = AgentSimulator()
    monitor = EventMonitor()
    detector = RuleBasedDetector(max_requests=2)
    risk_assessor = RiskAssessor()

    events = simulator.generate_suspicious_events()
    monitor.collect_events(events)

    collected_events = monitor.get_events()
    anomalies = detector.detect(collected_events)
    risk = risk_assessor.assess(anomalies)

    anomaly_types = [anomaly["type"] for anomaly in anomalies]

    assert len(collected_events) == 6
    assert "excessive_requests" in anomaly_types
    assert "restricted_access" in anomaly_types
    assert "repeated_failures" in anomaly_types
    assert risk["risk_score"] == 100
    assert risk["risk_level"] == "Critical"
    assert risk["total_anomalies"] == 3
