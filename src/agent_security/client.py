
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from agent_security.events import AgentEvent


# Load environment variables from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class AgentSecurityClient:
    """Client for sending authenticated AI agent events."""

    def __init__(
        self,
        base_url="http://127.0.0.1:8000",
        timeout=10.0
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = os.getenv("AGENT_SENTINEL_API_KEY")

    def _auth_headers(self):
        """Return authentication headers for protected endpoints."""

        if not self.api_key:
            raise RuntimeError(
                "API key not found. Configure AGENT_SENTINEL_API_KEY "
                "in the project root .env file."
            )

        return {"X-API-Key": self.api_key}

    def send_event(self, event: AgentEvent):
        response = httpx.post(
            f"{self.base_url}/events",
            json=event.model_dump(mode="json"),
            headers=self._auth_headers(),
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def send_events(self, events: list[AgentEvent]):
        if not events:
            raise ValueError("Event batch cannot be empty.")

        response = httpx.post(
            f"{self.base_url}/events/batch",
            json=[event.model_dump(mode="json") for event in events],
            headers=self._auth_headers(),
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def analyze(self, agent_id: str, session_id: str):
        response = httpx.get(
            f"{self.base_url}/analyze",
            params={
                "agent_id": agent_id,
                "session_id": session_id
            },
            headers=self._auth_headers(),
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def health_check(self):
        # Health endpoint is public.
        response = httpx.get(
            f"{self.base_url}/health",
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()
