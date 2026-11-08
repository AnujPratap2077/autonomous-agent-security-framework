
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query

from agent_security.events import AgentEvent
from agent_security.collectors.monitor import EventMonitor
from agent_security.database import EventDatabase
from agent_security.detectors.rule_engine import RuleBasedDetector
from agent_security.risk.assessor import RiskAssessor

from agent_security.baselines.manager import AgentBaselineManager
from agent_security.baselines.features import BehaviourFeatureExtractor
from agent_security.baselines.deviation import BehaviourDeviationDetector


# --------------------------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("AGENT_SENTINEL_API_KEY")


# --------------------------------------------------
# API KEY AUTHENTICATION
# --------------------------------------------------

def verify_api_key(
    api_key: str | None = Header(default=None, alias="X-API-Key")
):
    """Require a valid API key for protected endpoints."""

    if not API_KEY:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured."
        )

    if not api_key or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key."
        )


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Behavioral Anomaly Detection Framework",
    description="Live monitoring and behavioral risk analysis for autonomous AI agents.",
    version="0.4.0"
)


# --------------------------------------------------
# HTTP REQUEST BODY SIZE PROTECTION
# --------------------------------------------------

MAX_REQUEST_BODY_SIZE = 1_048_576  # 1 MB


class RequestBodyLimitMiddleware:
    """Reject HTTP requests exceeding the configured body-size limit."""

    def __init__(self, app, max_body_size: int):
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body_chunks = []
        total_size = 0

        while True:
            message = await receive()

            if message["type"] == "http.disconnect":
                return

            if message["type"] != "http.request":
                continue

            chunk = message.get("body", b"")
            total_size += len(chunk)

            if total_size > self.max_body_size:
                response_body = (
                    b'{"detail":"Request body exceeds the 1 MB limit."}'
                )

                await send({
                    "type": "http.response.start",
                    "status": 413,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (
                            b"content-length",
                            str(len(response_body)).encode("ascii")
                        )
                    ]
                })

                await send({
                    "type": "http.response.body",
                    "body": response_body
                })
                return

            body_chunks.append(chunk)

            if not message.get("more_body", False):
                break

        body = b"".join(body_chunks)
        body_sent = False

        async def replay_receive():
            nonlocal body_sent

            if not body_sent:
                body_sent = True
                return {
                    "type": "http.request",
                    "body": body,
                    "more_body": False
                }

            return await receive()

        await self.app(scope, replay_receive, send)


app.add_middleware(
    RequestBodyLimitMiddleware,
    max_body_size=MAX_REQUEST_BODY_SIZE
)


# --------------------------------------------------
# DATABASE AND COMPONENT INITIALIZATION
# --------------------------------------------------

DATABASE_PATH = PROJECT_ROOT / "data" / "agent_events.db"

database = EventDatabase(database_path=DATABASE_PATH)
monitor = EventMonitor(database=database)

detector = RuleBasedDetector(max_requests=2)
risk_assessor = RiskAssessor()

baseline_manager = AgentBaselineManager(min_sessions=5)
feature_extractor = BehaviourFeatureExtractor()
deviation_detector = BehaviourDeviationDetector(threshold=3.0)


# --------------------------------------------------
# API ENDPOINTS
# --------------------------------------------------

@app.get("/health")
def health_check():
    # Public endpoint: no API key required.
    return {
        "status": "online",
        "message": "Agent monitoring API is running."
    }


@app.post("/events", dependencies=[Depends(verify_api_key)])
def receive_event(event: AgentEvent):
    monitor.collect_event(event)

    return {
        "message": "Event received successfully.",
        "event_id": event.event_id,
        "total_events": len(monitor.get_events())
    }


# --------------------------------------------------
# BATCH SIZE PROTECTION
# --------------------------------------------------

MAX_BATCH_SIZE = 1000


@app.post("/events/batch", dependencies=[Depends(verify_api_key)])
def receive_event_batch(events: list[AgentEvent]):

    if not events:
        raise HTTPException(
            status_code=400,
            detail="Event batch cannot be empty."
        )

    if len(events) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Batch cannot contain more than {MAX_BATCH_SIZE} events."
        )

    monitor.collect_events(events)

    return {
        "message": "Event batch received successfully.",
        "events_received": len(events),
        "total_events": len(monitor.get_events())
    }


@app.get("/events", dependencies=[Depends(verify_api_key)])
def get_events():
    return monitor.get_events()


@app.get("/summary", dependencies=[Depends(verify_api_key)])
def get_summary():
    return monitor.get_summary()


# --------------------------------------------------
# HYBRID ANOMALY ANALYSIS
# --------------------------------------------------

@app.get("/analyze", dependencies=[Depends(verify_api_key)])
def analyze_agent(
    agent_id: str = Query(min_length=1, max_length=128),
    session_id: str = Query(min_length=1, max_length=128)
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

    # Rule-based anomaly detection
    rule_anomalies = detector.detect(session_events)

    # Behavioural baseline analysis
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

    # Combined anomaly analysis
    all_anomalies = rule_anomalies + behavioural_anomalies

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
                baseline["sessions_used"] if baseline is not None else 0
            ),
            "minimum_sessions_required": 5
        },
        "anomalies": all_anomalies,
        "risk_assessment": risk
    }
