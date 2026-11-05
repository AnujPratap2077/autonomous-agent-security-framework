from agent_security.risk.assessor import RiskAssessor


def test_no_anomalies():
    assessor = RiskAssessor()

    result = assessor.assess([])

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["total_anomalies"] == 0


def test_excessive_requests():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "excessive_requests"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 30
    assert result["risk_level"] == "Medium"


def test_restricted_access():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "restricted_access"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 50
    assert result["risk_level"] == "High"


def test_combined_anomalies():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "excessive_requests"},
        {"type": "restricted_access"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 80
    assert result["risk_level"] == "Critical"


def test_risk_score_capped_at_100():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "restricted_access"},
        {"type": "restricted_access"},
        {"type": "excessive_requests"}
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 100


def test_multiple_behavioural_deviations_count_once():
    assessor = RiskAssessor()

    anomalies = [
        {"type": "behavioural_deviation"},
        {"type": "behavioural_deviation"},
        {"type": "behavioural_deviation"},
    ]

    result = assessor.assess(anomalies)

    assert result["risk_score"] == 25
    assert result["risk_level"] == "Medium"
    assert result["total_anomalies"] == 3