
from agent_security.simulator import AgentSimulator
from agent_security.collectors.monitor import EventMonitor
from agent_security.detectors.rule_engine import RuleBasedDetector


def main():
    print("\n==========================================")
    print(" BEHAVIORAL ANOMALY DETECTION FRAMEWORK")
    print("==========================================")

    print("\nChoose an agent behaviour scenario:")
    print("1. Normal agent behaviour")
    print("2. Suspicious agent behaviour")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    simulator = AgentSimulator()
    monitor = EventMonitor()

    # Lower threshold for this small demonstration dataset.
    detector = RuleBasedDetector(max_requests=2)

    if choice == "1":
        events = simulator.generate_normal_events()
        scenario = "Normal"

    elif choice == "2":
        events = simulator.generate_suspicious_events()
        scenario = "Suspicious"

    else:
        print("\nInvalid choice. Please select 1 or 2.")
        return

    # Step 1: Collect agent events
    monitor.collect_events(events)

    # Step 2: Analyse collected events
    collected_events = monitor.get_events()
    anomalies = detector.detect(collected_events)

    # Step 3: Get activity statistics
    summary = monitor.get_summary()

    print(f"\nSelected scenario: {scenario}")

    print("\n---------- AGENT EVENTS ----------")
    for event in collected_events:
        print(f"{event.action:25} | {event.status}")

    print("\n---------- ACTIVITY SUMMARY ----------")
    print(f"Total events:      {summary['total_events']}")
    print(f"Successful events: {summary['successful_events']}")
    print(f"Failed events:     {summary['failed_events']}")
    print(f"Blocked events:    {summary['blocked_events']}")

    print("\n---------- DETECTION RESULTS ----------")

    if anomalies:
        print(f"Anomalies detected: {len(anomalies)}")

        for number, anomaly in enumerate(anomalies, start=1):
            print(f"\n{number}. {anomaly['type'].replace('_', ' ').title()}")
            print(f"Severity: {anomaly['severity'].upper()}")
            print(f"Reason: {anomaly['message']}")
    else:
        print("No suspicious behaviour detected.")

    print("\n==========================================")
    print(" DEMONSTRATION COMPLETED")
    print("==========================================")


if __name__ == "__main__":
    main()
