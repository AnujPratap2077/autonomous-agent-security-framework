
from agent_security.events import AgentEvent


class AgentSimulator:
    """Generates sample events for normal and suspicious AI agent behaviour."""

    def __init__(self, agent_id="demo-agent-001",
                 session_id="demo-session-001"):

        self.agent_id = agent_id
        self.session_id = session_id

    def generate_normal_events(self):
        """Generate events representing normal agent behaviour."""

        return [
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="file_read",
                tool_name="file_reader",
                status="success",
                duration_ms=120
            ),
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="web_search",
                tool_name="search_tool",
                status="success",
                duration_ms=350
            ),
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="text_summarization",
                tool_name="summarizer",
                status="success",
                duration_ms=80
            )
        ]

    def generate_suspicious_events(self):
        """Generate events representing suspicious agent behaviour."""

        return [
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="api_request",
                tool_name="api_tool",
                status="success",
                duration_ms=20
            ),
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="api_request",
                tool_name="api_tool",
                status="success",
                duration_ms=18
            ),
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="api_request",
                tool_name="api_tool",
                status="success",
                duration_ms=15
            ),
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="restricted_file_access",
                tool_name="file_reader",
                status="blocked",
                duration_ms=10,
                error_message="Permission denied"
            ),
            AgentEvent(
                agent_id=self.agent_id,
                session_id=self.session_id,
                action="database_access",
                tool_name="database_tool",
                status="failure",
                duration_ms=25,
                error_message="Unauthorized access"
            )
        ]
