from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models import WiFiScan

router = APIRouter()


@router.get("/WiFiScans")
async def get_WiFiScans(limit: int = 50, db: Session = Depends(get_db)):
    """Return the most recent WiFiScan rows as plain dictionaries."""
    rows = db.query(WiFiScan).order_by(WiFiScan.id.desc()).limit(limit).all()
    return [
        {
            "id": n.id,
            "ssid": n.ssid,
            "rssi": n.rssi,
            # Add more fields as needed: "bssid": n.bssid, etc.
        }
        for n in rows
    ]
