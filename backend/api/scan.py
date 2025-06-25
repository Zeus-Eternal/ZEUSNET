from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import WiFiScan
from datetime import datetime
from pydantic import BaseModel
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ScanModel(BaseModel):
    ssid: str
    bssid: str
    rssi: int
    auth: str
    channel: int
    timestamp: datetime

@router.post("/scan")
def insert_scan(scans: List[ScanModel], db: Session = Depends(get_db)):
    for s in scans:
        db.add(WiFiScan(**s.dict()))
    db.commit()
    return {"status": "ok", "count": len(scans)}
