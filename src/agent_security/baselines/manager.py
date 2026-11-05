
from agent_security.baselines.features import BehaviourFeatureExtractor
from agent_security.baselines.builder import BehaviourBaselineBuilder


class AgentBaselineManager:
    """Builds behavioural baselines from an agent's historical sessions."""

    def __init__(self, min_sessions=5):
        self.feature_extractor = BehaviourFeatureExtractor()
        self.baseline_builder = BehaviourBaselineBuilder(
            min_sessions=min_sessions
        )

    def build_baseline(self, events, agent_id, exclude_session_id=None):
        """Build a baseline using only the agent's historical sessions."""

        agent_sessions = {}

        for event in events:
            if event.agent_id != agent_id:
                continue

            if event.session_id == exclude_session_id:
                continue

            agent_sessions.setdefault(event.session_id, []).append(event)

        historical_features = [
            self.feature_extractor.extract(session_events)
            for session_events in agent_sessions.values()
        ]

        if len(historical_features) < self.baseline_builder.min_sessions:
            return None

        return self.baseline_builder.build(historical_features)
