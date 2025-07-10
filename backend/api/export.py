from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import WiFiScan
from datetime import datetime
from io import StringIO
import csv

router = APIRouter()


@router.get("/export/csv")
def export_csv(from_date: str, to_date: str, db: Session = Depends(get_db)):
    start = datetime.fromisoformat(from_date)
    end = datetime.fromisoformat(to_date)
    scans = db.query(WiFiScan).filter(WiFiScan.timestamp.between(start, end)).all()

    def iter_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["SSID", "BSSID", "RSSI", "Auth", "Channel", "Timestamp"])
        for s in scans:
            writer.writerow([s.ssid, s.bssid, s.rssi, s.auth, s.channel, s.timestamp])
        output.seek(0)
        yield output.read()

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=zeusnet_export_{from_date}_to_{to_date}.csv"
        },
    )
