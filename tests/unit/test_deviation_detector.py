
import pytest

from agent_security.baselines.deviation import BehaviourDeviationDetector


def test_normal_behaviour_is_not_flagged():
    detector = BehaviourDeviationDetector()

    current = {"api_requests": 6}

    baseline = {
        "features": {
            "api_requests": {
                "mean": 5.8,
                "std_dev": 1.0
            }
        }
    }

    result = detector.detect(current, baseline)

    assert result == []


def test_unusual_behaviour_is_detected():
    detector = BehaviourDeviationDetector()

    current = {"api_requests": 30}

    baseline = {
        "features": {
            "api_requests": {
                "mean": 5.8,
                "std_dev": 1.0
            }
        }
    }

    result = detector.detect(current, baseline)

    assert len(result) == 1
    assert result[0]["type"] == "behavioural_deviation"
    assert result[0]["feature"] == "api_requests"
    assert result[0]["z_score"] == 24.2


def test_constant_baseline_detects_changed_value():
    detector = BehaviourDeviationDetector()

    current = {"api_requests": 15}

    baseline = {
        "features": {
            "api_requests": {
                "mean": 5,
                "std_dev": 0
            }
        }
    }

    result = detector.detect(current, baseline)

    assert len(result) == 1
    assert result[0]["z_score"] is None


def test_missing_feature_is_ignored():
    detector = BehaviourDeviationDetector()

    current = {"api_requests": 30}

    baseline = {
        "features": {}
    }

    result = detector.detect(current, baseline)

    assert result == []


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError):
        BehaviourDeviationDetector(threshold=0)
