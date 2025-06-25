from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.alerts.anomaly import detect_anomalies
from backend.alerts.mac_tracker import track_devices
from backend.alerts.rogue_ap import detect_rogue_aps

router = APIRouter()


@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """Aggregate all alert types into a single list."""
    alerts = []
    alerts.extend(detect_anomalies(db))
    alerts.extend(detect_rogue_aps(db))
    alerts.extend(track_devices(db))
    return alerts
