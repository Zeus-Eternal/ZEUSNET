from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import WiFiScan

router = APIRouter()


@router.get("/networks")
def get_networks(limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    scans = db.query(WiFiScan).order_by(WiFiScan.timestamp.desc()).limit(limit).all()
    return [s.__dict__ for s in scans]
