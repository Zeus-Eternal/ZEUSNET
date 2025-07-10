from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import WiFiScan
from backend import settings

router = APIRouter()


@router.get("/networks")
def get_networks(
    limit: int | None = Query(50, le=500),
    auth: str | None = None,
    ssid: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(WiFiScan)
    if auth:
        query = query.filter(WiFiScan.auth == auth)
    if ssid:
        query = query.filter(WiFiScan.ssid == ssid)
    query = query.order_by(WiFiScan.timestamp.desc())
    if limit:
        query = query.limit(limit)
    scans = query.all()

    def _to_dict(s: WiFiScan) -> dict:
        base = {
            "id": s.id,
            "ssid": s.ssid,
            "rssi": s.rssi,
        }
        if settings.ZEUSNET_MODE == "AGGRESSIVE":
            base.update(
                {
                    "bssid": s.bssid,
                    "auth": s.auth,
                    "channel": s.channel,
                    "timestamp": s.timestamp,
                }
            )
        return base

    return [_to_dict(s) for s in scans]
