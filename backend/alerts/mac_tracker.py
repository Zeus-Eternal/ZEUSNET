# mac_tracker.py
from backend.db import get_db
from backend.models import DeviceSeen
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def track_devices(db: Session):
    now = datetime.utcnow()
    threshold = now - timedelta(days=7)
    records = db.query(DeviceSeen).filter(DeviceSeen.last_seen >= threshold).all()

    results = []
    for r in records:
        results.append({
            "mac": r.mac,
            "first_seen": r.first_seen,
            "last_seen": r.last_seen,
            "vendor": r.vendor,
            "flag": "New Device" if r.first_seen > threshold else "Known"
        })
    return results
