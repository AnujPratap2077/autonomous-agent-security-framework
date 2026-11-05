
import pytest

from agent_security.baselines.builder import BehaviourBaselineBuilder


def test_build_baseline_successfully():
    builder = BehaviourBaselineBuilder()

    historical_features = [
        {"api_requests": 5},
        {"api_requests": 6},
        {"api_requests": 5},
        {"api_requests": 7},
        {"api_requests": 6},
    ]

    result = builder.build(historical_features)

    assert result["sessions_used"] == 5
    assert result["features"]["api_requests"]["mean"] == 5.8
    assert result["features"]["api_requests"]["std_dev"] == 0.748


def test_baseline_rejects_insufficient_sessions():
    builder = BehaviourBaselineBuilder()

    historical_features = [
        {"api_requests": 5},
        {"api_requests": 6},
    ]

    with pytest.raises(ValueError):
        builder.build(historical_features)


def test_custom_minimum_sessions():
    builder = BehaviourBaselineBuilder(min_sessions=3)

    historical_features = [
        {"api_requests": 5},
        {"api_requests": 6},
        {"api_requests": 7},
    ]

    result = builder.build(historical_features)

    assert result["sessions_used"] == 3


def test_minimum_sessions_cannot_be_less_than_two():
    with pytest.raises(ValueError):
        BehaviourBaselineBuilder(min_sessions=1)
