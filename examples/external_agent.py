
from uuid import uuid4

from agent_security.client import AgentSecurityClient
from agent_security.simulator import AgentSimulator


AGENT_ID = "external-agent-001"


def main():
    client = AgentSecurityClient()

    # Generate unique session IDs for every simulation run.
    run_id = uuid4().hex[:8]

    normal_session = f"normal-session-{run_id}"
    suspicious_session = f"suspicious-session-{run_id}"

    print("\n======================================")
    print(" EXTERNAL AI AGENT SIMULATION")
    print("======================================")

    health = client.health_check()
    print("\nAPI Status:", health["status"])

    # Normal agent behaviour
    print("\n[1] Sending normal agent activities...")

    normal_simulator = AgentSimulator(
        agent_id=AGENT_ID,
        session_id=normal_session
    )

    normal_events = normal_simulator.generate_normal_events()
    result = client.send_events(normal_events)

    print("Events sent:", result["events_received"])

    normal_report = client.analyze(AGENT_ID, normal_session)

    print("\nNormal Behaviour Risk Report:")
    print(normal_report["risk_assessment"])

    # Suspicious agent behaviour
    print("\n[2] Sending suspicious agent activities...")

    suspicious_simulator = AgentSimulator(
        agent_id=AGENT_ID,
        session_id=suspicious_session
    )

    suspicious_events = suspicious_simulator.generate_suspicious_events()
    result = client.send_events(suspicious_events)

    print("Events sent:", result["events_received"])

    suspicious_report = client.analyze(AGENT_ID, suspicious_session)

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
