
from agent_security.events import AgentEvent


class RuleBasedDetector:
    """Detects suspicious AI agent behaviour using simple rules."""

    def __init__(self, max_requests=5):
        self.max_requests = max_requests

    def detect(self, events: list[AgentEvent]):
        """Analyse events and return detected anomalies."""

        anomalies = []

        # Rule 1: Detect excessive API requests
        api_requests = [
            event for event in events
            if event.action == "api_request"
        ]

        if len(api_requests) > self.max_requests:
            anomalies.append({
                "type": "excessive_requests",
                "severity": "high",
                "message": (
                    f"Agent generated {len(api_requests)} API requests. "
                    f"Allowed threshold is {self.max_requests}."
                )
            })

        # Rule 2: Detect restricted resource access
        for event in events:
            if event.status == "blocked":
                anomalies.append({
                    "type": "restricted_access",
                    "severity": "high",
                    "message": (
                        f"Agent attempted a restricted action: "
                        f"{event.action}"
                    )
                })

        # Rule 3: Detect repeated failures
        failures = [
            event for event in events
            if event.status == "failure"
        ]

        if len(failures) >= 2:
            anomalies.append({
                "type": "repeated_failures",
                "severity": "medium",
                "message": (
                    f"Agent experienced {len(failures)} failed actions."
                )
            })

        return anomalies
