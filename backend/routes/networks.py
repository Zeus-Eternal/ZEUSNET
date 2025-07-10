from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models import WiFiScan

router = APIRouter()


@router.get("/WiFiScans")
async def get_WiFiScans(limit: int = 50, db: Session = Depends(get_db)):
    """Return the most recent WiFi scans."""
    scans = db.query(WiFiScan).order_by(WiFiScan.id.desc()).limit(limit).all()
    return [s.to_dict() for s in scans]
