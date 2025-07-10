from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import WiFiScan

router = APIRouter()

@router.get("/WiFiScans")
async def get_WiFiScans(limit: int = 50, db: Session = Depends(get_db)):
    # Query for most recent N WiFiScans; customize for your schema
    rows = db.query(WiFiScan).order_by(WiFiScan.id.desc()).limit(limit).all()
    # Convert ORM rows to plain dicts
    return [
        {
            "id": n.id,
            "ssid": n.ssid,
            "rssi": n.rssi,
            # Add more fields as needed: "bssid": n.bssid, etc.
        }
        for n in rows
    ]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import WiFiScan

router = APIRouter()

@router.get("/WiFiScans")
async def get_WiFiScans(limit: int = 50, db: Session = Depends(get_db)):
    scans = db.query(WiFiScan).order_by(WiFiScan.id.desc()).limit(limit).all()
    return [s.to_dict() for s in scans]
