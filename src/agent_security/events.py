
from datetime import datetime, timezone
from uuid import uuid4
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class AgentEvent(BaseModel):
    """Represents an observable action performed by an AI agent."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()))

    agent_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    action: str = Field(min_length=1, max_length=128)
    tool_name: str | None = Field(default=None, max_length=128)

    status: Literal["success", "failure", "blocked"]

    duration_ms: float = Field(default=0.0, ge=0)

    error_message: str | None = Field(default=None, max_length=1000)
