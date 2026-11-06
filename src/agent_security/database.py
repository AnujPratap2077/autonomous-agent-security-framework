
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from agent_security.events import AgentEvent


class EventDatabase:
    """Handles persistent storage and retrieval of agent events using SQLite."""

    def __init__(self, database_path=":memory:"):
        self._use_uri = database_path == ":memory:"

        if self._use_uri:
            self.database_path = (
                f"file:agent_events_{uuid4().hex}?mode=memory&cache=shared"
            )
            self._anchor_connection = sqlite3.connect(
                self.database_path,
                uri=True,
                check_same_thread=False
            )
        else:
            self.database_path = str(database_path)
            Path(self.database_path).parent.mkdir(
                parents=True,
                exist_ok=True
            )
            self._anchor_connection = None

        self._create_table()

    @contextmanager
    def _get_connection(self):
        """Create and safely close a database connection."""

        connection = sqlite3.connect(
            self.database_path,
            uri=self._use_uri,
            timeout=10,
            check_same_thread=False
        )
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _create_table(self):
        """Create the events table if it does not exist."""

        with self._get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    tool_name TEXT,
                    status TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    error_message TEXT
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_events_agent_session
                ON events (agent_id, session_id)
                """
            )

    def save_event(self, event: AgentEvent):
        """Save one agent event."""

        with self._get_connection() as connection:
            connection.execute(
                """
                INSERT INTO events (
                    event_id, agent_id, session_id, timestamp,
                    action, tool_name, status, duration_ms, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.agent_id,
                    event.session_id,
                    event.timestamp.isoformat(),
                    event.action,
                    event.tool_name,
                    event.status,
                    event.duration_ms,
                    event.error_message
                )
            )

    def save_events(self, events: list[AgentEvent]):
        """Save multiple agent events in one transaction."""

        if not events:
            raise ValueError("Event batch cannot be empty.")

        records = [
            (
                event.event_id,
                event.agent_id,
                event.session_id,
                event.timestamp.isoformat(),
                event.action,
                event.tool_name,
                event.status,
                event.duration_ms,
                event.error_message
            )
            for event in events
        ]

        with self._get_connection() as connection:
            connection.executemany(
                """
                INSERT INTO events (
                    event_id, agent_id, session_id, timestamp,
                    action, tool_name, status, duration_ms, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                records
            )

    def get_events(self):
        """Retrieve all stored events."""

        with self._get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM events ORDER BY rowid"
            ).fetchall()

        return [
            AgentEvent.model_validate(dict(row))
            for row in rows
        ]

    def count_events(self):
        """Return the total number of stored events."""

        with self._get_connection() as connection:
            result = connection.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()

        return result[0]

    def clear_events(self):
        """Delete all stored events."""

        with self._get_connection() as connection:
            connection.execute("DELETE FROM events")

    def close(self):
        """Close the shared in-memory database anchor."""

        if self._anchor_connection is not None:
            self._anchor_connection.close()
            self._anchor_connection = None
