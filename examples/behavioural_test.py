import httpx


BASE_URL = "http://127.0.0.1:8000"

AGENT_ID = "behaviour-test-agent"


def send_session(session_id, api_requests):
    events = []

    for _ in range(api_requests):
        events.append({
            "agent_id": AGENT_ID,
            "session_id": session_id,
            "action": "api_request",
            "tool_name": "test-api",
            "status": "success",
            "duration_ms": 100
        })

    response = httpx.post(
        f"{BASE_URL}/events/batch",
        json=events
    )

    response.raise_for_status()

    print(
        f"Session {session_id}: "
        f"{api_requests} API requests sent."
    )


def main():

    print("\n======================================")
    print(" BEHAVIOURAL ANOMALY TEST")
    print("======================================")

    print("\n[1] Sending historical behaviour...")

    for i in range(1, 6):
        send_session(
            session_id=f"history-{i}",
            api_requests=1
        )

    print("\n[2] Sending unusual current behaviour...")

    send_session(
        session_id="current-session",
        api_requests=10
    )

    print("\n[3] Analysing agent behaviour...")

    response = httpx.get(
        f"{BASE_URL}/analyze",
        params={
            "agent_id": AGENT_ID,
            "session_id": "current-session"
        }
    )

    response.raise_for_status()

    result = response.json()

    print("\nBaseline Analysis:")
    print(result["baseline_analysis"])

    print("\nBehavioural Anomalies:")
    for anomaly in result["behavioural_anomalies"]:
        print(anomaly)

    print("\nFinal Risk Assessment:")
    print(result["risk_assessment"])

    print("\n======================================")
    print(" TEST COMPLETED")
    print("======================================")


if __name__ == "__main__":
    main()