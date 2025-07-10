"""AnomalyGuard agent.

Runs statistical and ML checks over collected signal metrics to flag
abnormal activity. Current implementation delegates to ``alerts.anomaly``.
"""

from sqlalchemy.orm import Session

from backend.alerts.anomaly import detect_anomalies
from backend.db import SessionLocal


class AnomalyGuard:
    """Analyse stored Wi-Fi scans and generate alerts."""

    def __init__(self, db_session_factory=SessionLocal) -> None:
        self.db_session_factory = db_session_factory

    def scan(self) -> list[dict]:
        """Run anomaly detection over recent scans."""
        session: Session = self.db_session_factory()
        try:
            return detect_anomalies(session)
        finally:
            session.close()
