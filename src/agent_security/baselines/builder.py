
from statistics import mean, pstdev


class BehaviourBaselineBuilder:
    """Builds an agent-specific behavioural baseline."""

    def __init__(self, min_sessions=5):
        if min_sessions < 2:
            raise ValueError("Minimum sessions must be at least 2.")

        self.min_sessions = min_sessions

    def build(self, historical_features: list[dict]) -> dict:
        """Calculate mean and standard deviation of historical features."""

        if len(historical_features) < self.min_sessions:
            raise ValueError(
                f"At least {self.min_sessions} historical sessions "
                "are required to build a baseline."
            )

        feature_names = historical_features[0].keys()

        baseline = {}

        for feature in feature_names:
            values = [
                session[feature]
                for session in historical_features
            ]

            baseline[feature] = {
                "mean": round(mean(values), 3),
                "std_dev": round(pstdev(values), 3)
            }

        return {
            "sessions_used": len(historical_features),
            "features": baseline
        }
