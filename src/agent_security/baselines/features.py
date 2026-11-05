
from agent_security.events import AgentEvent


class BehaviourFeatureExtractor:
    """Extracts measurable behavioural features from agent events."""

    def extract(self, events: list[AgentEvent]) -> dict:
        if not events:
            raise ValueError("Cannot extract features from an empty event list.")

        total = len(events)

        successful = sum(
            event.status == "success" for event in events
        )
        failed = sum(
            event.status == "failure" for event in events
        )
        blocked = sum(
            event.status == "blocked" for event in events
        )

        api_requests = sum(
            event.action == "api_request" for event in events
        )

        unique_tools = len({
            event.tool_name
            for event in events
            if event.tool_name is not None
        })

        return {
            "total_actions": total,
            "api_requests": api_requests,
            "successful_actions": successful,
            "failed_actions": failed,
            "blocked_actions": blocked,
            "failure_rate": round(failed / total, 3),
            "blocked_rate": round(blocked / total, 3),
            "unique_tools": unique_tools
        }
