from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import WiFiScan

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/networks")
def get_networks(limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    scans = db.query(WiFiScan).order_by(WiFiScan.timestamp.desc()).limit(limit).all()
    return [s.__dict__ for s in scans]
