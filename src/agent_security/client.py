
import httpx

from agent_security.events import AgentEvent


class AgentSecurityClient:
    """Client for sending AI agent events to the security framework."""

    def __init__(self, base_url="http://127.0.0.1:8000", timeout=10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def send_event(self, event: AgentEvent):
        """Send one agent event to the monitoring API."""

        response = httpx.post(
            f"{self.base_url}/events",
            json=event.model_dump(mode="json"),
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def send_events(self, events: list[AgentEvent]):
        """Send multiple agent events in one batch."""

        if not events:
            raise ValueError("Event batch cannot be empty.")

        response = httpx.post(
            f"{self.base_url}/events/batch",
            json=[
                event.model_dump(mode="json")
                for event in events
            ],
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def analyze(self, agent_id: str, session_id: str):
        """Request a security analysis for an agent session."""

        response = httpx.get(
            f"{self.base_url}/analyze",
            params={
                "agent_id": agent_id,
                "session_id": session_id
            },
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def health_check(self):
        """Check whether the security API is available."""

        response = httpx.get(
            f"{self.base_url}/health",
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()
