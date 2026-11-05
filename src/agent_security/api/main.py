
from fastapi import FastAPI, HTTPException, Query

from agent_security.events import AgentEvent
from agent_security.collectors.monitor import EventMonitor
from agent_security.detectors.rule_engine import RuleBasedDetector
from agent_security.risk.assessor import RiskAssessor


app = FastAPI(
    title="Behavioral Anomaly Detection Framework",
    description="Live monitoring and behavioral risk analysis for autonomous AI agents.",
    version="0.3.0"
)

monitor = EventMonitor()
detector = RuleBasedDetector(max_requests=2)
risk_assessor = RiskAssessor()


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

    anomalies = detector.detect(session_events)
    risk = risk_assessor.assess(anomalies)

    return {
        "agent_id": agent_id,
        "session_id": session_id,
        "total_events": len(session_events),
        "anomalies": anomalies,
        "risk_assessment": risk
    }
