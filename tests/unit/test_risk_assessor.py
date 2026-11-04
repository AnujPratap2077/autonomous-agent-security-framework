
from agent_security.risk.assessor import RiskAssessor


def test_no_anomalies_has_zero_risk():
    assessor = RiskAssessor()

    result = assessor.assess([])

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["total_anomalies"] == 0


def test_excessive_requests_risk():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "excessive_requests"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 30
    assert result["risk_level"] == "Medium"


def test_restricted_access_risk():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "restricted_access"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 50
    assert result["risk_level"] == "High"


def test_combined_anomalies_critical_risk():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "excessive_requests"},
        {"type": "restricted_access"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 80
    assert result["risk_level"] == "Critical"
    assert result["total_anomalies"] == 2


def test_risk_score_never_exceeds_100():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "excessive_requests"},
        {"type": "restricted_access"},
        {"type": "repeated_failures"},
        {"type": "restricted_access"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 100
