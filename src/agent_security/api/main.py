from fastapi import FastAPI, HTTPException, Query

from agent_security.events import AgentEvent
from agent_security.collectors.monitor import EventMonitor
from agent_security.detectors.rule_engine import RuleBasedDetector
from agent_security.risk.assessor import RiskAssessor

from agent_security.baselines.manager import AgentBaselineManager
from agent_security.baselines.features import BehaviourFeatureExtractor
from agent_security.baselines.deviation import BehaviourDeviationDetector


app = FastAPI(
    title="Behavioral Anomaly Detection Framework",
    description="Live monitoring and behavioral risk analysis for autonomous AI agents.",
    version="0.4.0"
)

monitor = EventMonitor()
detector = RuleBasedDetector(max_requests=2)
risk_assessor = RiskAssessor()

baseline_manager = AgentBaselineManager(min_sessions=5)
feature_extractor = BehaviourFeatureExtractor()
deviation_detector = BehaviourDeviationDetector(threshold=3.0)


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "message": "Agent monitoring API is running."
    }


@app.post("/events")
def receive_event(event: AgentEvent):
    monitor.collect_event(event)

    return {
        "message": "Event received successfully.",
        "event_id": event.event_id,
        "total_events": len(monitor.get_events())
    }


@app.post("/events/batch")
def receive_event_batch(events: list[AgentEvent]):
    if not events:
        raise HTTPException(
            status_code=400,
            detail="Event batch cannot be empty."
        )

    monitor.collect_events(events)

    return {
        "message": "Event batch received successfully.",
        "events_received": len(events),
        "total_events": len(monitor.get_events())
    }


@app.get("/events")
def get_events():
    return monitor.get_events()


@app.get("/summary")
def get_summary():
    return monitor.get_summary()


@app.get("/analyze")
def analyze_agent(
    agent_id: str = Query(min_length=1),
    session_id: str = Query(min_length=1)
):
    all_events = monitor.get_events()

    session_events = [
        event for event in all_events
        if event.agent_id == agent_id
        and event.session_id == session_id
    ]

    if not session_events:
        raise HTTPException(
            status_code=404,
            detail="No events found for the specified agent and session."
        )

    # Layer 1: Existing rule-based detection.
    rule_anomalies = detector.detect(session_events)

    # Layer 2: Historical behavioural analysis.
    baseline = baseline_manager.build_baseline(
        events=all_events,
        agent_id=agent_id,
        exclude_session_id=session_id
    )

    behavioural_anomalies = []
    baseline_status = "unavailable"

    if baseline is not None:
        current_features = feature_extractor.extract(session_events)

        behavioural_anomalies = deviation_detector.detect(
            current_features=current_features,
            baseline=baseline
        )

        baseline_status = "available"

    # Combine both detection layers.
    all_anomalies = rule_anomalies + behavioural_anomalies

    # Calculate overall risk.
    risk = risk_assessor.assess(all_anomalies)

    return {
        "agent_id": agent_id,
        "session_id": session_id,
        "total_events": len(session_events),

        "rule_based_anomalies": rule_anomalies,
        "behavioural_anomalies": behavioural_anomalies,

        "baseline_analysis": {
            "status": baseline_status,
            "sessions_used": (
                baseline["sessions_used"]
                if baseline is not None else 0
            ),
            "minimum_sessions_required": 5
        },

        "anomalies": all_anomalies,
        "risk_assessment": risk
    }