# rogue_ap.py
from backend.models import WiFiScan
from sqlalchemy.orm import Session


def detect_rogue_aps(db: Session):
    seen_ssids = {}
    rogue_aps = []

    scans = db.query(WiFiScan).order_by(WiFiScan.timestamp.desc()).all()
    for scan in scans:
        if scan.ssid not in seen_ssids:
            seen_ssids[scan.ssid] = scan.bssid
        elif seen_ssids[scan.ssid] != scan.bssid:
            rogue_aps.append(
                {
                    "ssid": scan.ssid,
                    "bssid": scan.bssid,
                    "timestamp": scan.timestamp,
                    "channel": scan.channel,
                    "alert": "Rogue AP detected – SSID conflict",
                }
            )

    return rogue_aps
