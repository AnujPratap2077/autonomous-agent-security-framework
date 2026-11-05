
from agent_security.client import AgentSecurityClient
from agent_security.events import AgentEvent


AGENT_ID = "external-agent-001"


def generate_normal_events(session_id):
    """Simulate normal autonomous agent activities."""

    return [
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="file_read",
            tool_name="file_reader",
            status="success",
            duration_ms=120
        ),
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="web_search",
            tool_name="search_tool",
            status="success",
            duration_ms=250
        ),
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="text_summarization",
            tool_name="summarizer",
            status="success",
            duration_ms=90
        )
    ]


def generate_suspicious_events(session_id):
    """Simulate suspicious autonomous agent activities."""

    return [
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="api_request",
            tool_name="api_tool",
            status="success",
            duration_ms=20
        ),
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="api_request",
            tool_name="api_tool",
            status="success",
            duration_ms=18
        ),
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="api_request",
            tool_name="api_tool",
            status="success",
            duration_ms=15
        ),
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="restricted_file_access",
            tool_name="file_reader",
            status="blocked",
            duration_ms=10,
            error_message="Permission denied"
        ),
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="database_access",
            tool_name="database_tool",
            status="failure",
            duration_ms=25,
            error_message="Unauthorized access"
        ),
        AgentEvent(
            agent_id=AGENT_ID,
            session_id=session_id,
            action="database_write",
            tool_name="database_tool",
            status="failure",
            duration_ms=30,
            error_message="Write operation failed"
        )
    ]


def main():
    client = AgentSecurityClient()

    print("\n======================================")
    print(" EXTERNAL AI AGENT SIMULATION")
    print("======================================")

    # Check API connection
    health = client.health_check()
    print("\nAPI Status:", health["status"])

    # Scenario 1: Normal behaviour
    normal_session = "normal-session-001"

    print("\n[1] Sending normal agent activities...")

    normal_events = generate_normal_events(normal_session)
    result = client.send_events(normal_events)

    print("Events sent:", result["events_received"])

    normal_report = client.analyze(
        AGENT_ID,
        normal_session
    )

    print("\nNormal Behaviour Risk Report:")
    print(normal_report["risk_assessment"])

    # Scenario 2: Suspicious behaviour
    suspicious_session = "suspicious-session-001"

    print("\n[2] Sending suspicious agent activities...")

    suspicious_events = generate_suspicious_events(
        suspicious_session
    )

    result = client.send_events(suspicious_events)

    print("Events sent:", result["events_received"])

    suspicious_report = client.analyze(
        AGENT_ID,
        suspicious_session
    )

    print("\nSuspicious Behaviour Risk Report:")
    print(suspicious_report["risk_assessment"])

    print("\nDetected Anomalies:")

    for anomaly in suspicious_report["anomalies"]:
        print("-", anomaly["type"], ":", anomaly["message"])

    print("\n======================================")
    print(" SIMULATION COMPLETED")
    print("======================================")


if __name__ == "__main__":
    main()
