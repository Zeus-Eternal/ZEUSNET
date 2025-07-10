import re
import subprocess
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator

from backend import settings

router = APIRouter()


class AttackModel(BaseModel):
    mode: str
    target: str | None = None
    channel: int | None = None
    iface: str | None = None

    @validator("target")
    def _validate_mac(cls, v, values):
        if values.get("mode") == "deauth" and v is not None:
            if not re.fullmatch(r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", v):
                raise ValueError("target must be a valid MAC for deauth attack")
        return v


class AttackService:
    """Lightweight wrapper around common NIC attack tools."""

    def __init__(self):
        self.active: dict[int, dict] = {}

    def _build_command(
        self, mode: str, target: str | None, channel: int | None, iface: str
    ) -> list[str]:
        if mode == "deauth" and target:
            return ["aireplay-ng", "--deauth", "10", "-a", target, iface]
        if mode == "rogue_ap":
            return ["echo", "rogue_ap"]
        if mode == "pmkid":
            return ["echo", "pmkid"]
        if mode == "probe":
            return ["python3", "scripts/probe_flood.py", "--target", target or "00:00:00:00:00:00", "--iface", iface]
        if mode == "syn_flood":
            return ["python3", "scripts/syn_flood.py", "--target", target or "127.0.0.1", "--iface", iface]
        if mode == "swarm":
            return ["echo", "swarm"]
        if mode == "survey":
            return ["echo", "survey"]
        if mode == "jam" and target:
            return ["echo", f"jam {target}"]
        raise HTTPException(status_code=400, detail="Invalid attack parameters")

    def launch(self, mode: str, target: str | None, channel: int | None, iface: str | None) -> int:
        if settings.ZEUSNET_MODE != "AGGRESSIVE":
            raise HTTPException(status_code=403, detail="Aggressive mode disabled")
        cmd = self._build_command(mode, target, channel, iface or "wlan0")
        proc = subprocess.Popen(cmd)
        self.active[proc.pid] = {"mode": mode, "target": target, "channel": channel, "iface": iface or "wlan0"}
        return proc.pid

    def status(self) -> dict:
        return self.active


attack_service = AttackService()


@router.post("/nic/attack")
def nic_attack(req: AttackModel):
    pid = attack_service.launch(req.mode, req.target, req.channel, req.iface)
    return {"status": "started", "pid": pid}


@router.get("/status")
def nic_status():
    return {
        "mode": settings.ZEUSNET_MODE,
        "active_attacks": attack_service.status(),
    }
