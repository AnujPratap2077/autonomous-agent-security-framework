
class BehaviourDeviationDetector:
    """Detects unusual behaviour using statistical Z-scores."""

    def __init__(self, threshold=3.0):
        if threshold <= 0:
            raise ValueError("Threshold must be greater than zero.")

        self.threshold = threshold

    def detect(self, current_features: dict, baseline: dict) -> list:
        anomalies = []

        baseline_features = baseline.get("features", {})

        for feature, current_value in current_features.items():

            if feature not in baseline_features:
                continue

            expected = baseline_features[feature]["mean"]
            std_dev = baseline_features[feature]["std_dev"]

            # Avoid division by zero when historical values are constant.
            if std_dev == 0:
                if current_value != expected:
                    anomalies.append({
                        "type": "behavioural_deviation",
                        "feature": feature,
                        "current_value": current_value,
                        "expected_value": expected,
                        "z_score": None,
                        "severity": "high",
                        "message": (
                            f"{feature} changed from its constant "
                            f"historical value of {expected} to "
                            f"{current_value}."
                        )
                    })
                continue

            z_score = (current_value - expected) / std_dev

            if abs(z_score) >= self.threshold:
                anomalies.append({
                    "type": "behavioural_deviation",
                    "feature": feature,
                    "current_value": current_value,
                    "expected_value": expected,
                    "z_score": round(z_score, 3),
                    "severity": "high",
                    "message": (
                        f"{feature} deviated significantly from "
                        f"its historical behaviour. "
                        f"Z-score: {z_score:.3f}."
                    )
                })

        return anomalies
