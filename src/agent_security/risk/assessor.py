class RiskAssessor:
    """Calculates an overall risk score from detected anomalies."""

    RISK_POINTS = {
        "excessive_requests": 30,
        "restricted_access": 50,
        "repeated_failures": 20,
        "behavioural_deviation": 25,
    }

    def assess(self, anomalies):
        """Calculate risk score and classify the risk level."""

        # Score traditional rule-based anomalies individually.
        score = sum(
            self.RISK_POINTS.get(anomaly["type"], 0)
            for anomaly in anomalies
            if anomaly["type"] != "behavioural_deviation"
        )

        # Count behavioural deviation only once per analysis.
        if any(
            anomaly["type"] == "behavioural_deviation"
            for anomaly in anomalies
        ):
            score += self.RISK_POINTS["behavioural_deviation"]

        # Risk score cannot exceed 100.
        score = min(score, 100)

        if score >= 80:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 20:
            level = "Medium"
        else:
            level = "Low"

        return {
            "risk_score": score,
            "risk_level": level,
            "total_anomalies": len(anomalies)
        }