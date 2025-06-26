from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess

from backend import settings

router = APIRouter()


class AttackModel(BaseModel):
    mode: str
    target: str | None = None
    channel: int | None = None


class AttackService:
    """Lightweight wrapper around common NIC attack tools."""

    def __init__(self):
        self.active: dict[int, dict] = {}

    def _build_command(
        self, mode: str, target: str | None, channel: int | None
    ) -> list[str]:
        if mode == "deauth" and target:
            return ["echo", f"deauth {target}"]
        if mode == "rogue_ap":
            return ["echo", "rogue_ap"]
        if mode == "pmkid":
            return ["echo", "pmkid"]
        if mode == "swarm":
            return ["echo", "swarm"]
        if mode == "survey":
            return ["echo", "survey"]
        if mode == "jam" and target:
            return ["echo", f"jam {target}"]
        raise HTTPException(status_code=400, detail="Invalid attack parameters")

    def launch(self, mode: str, target: str | None, channel: int | None) -> int:
        if settings.ZEUSNET_MODE != "AGGRESSIVE":
            raise HTTPException(status_code=403, detail="Aggressive mode disabled")
        cmd = self._build_command(mode, target, channel)
        proc = subprocess.Popen(cmd)
        self.active[proc.pid] = {"mode": mode, "target": target, "channel": channel}
        return proc.pid

    def status(self) -> dict:
        return self.active


attack_service = AttackService()


@router.post("/nic/attack")
def nic_attack(req: AttackModel):
    pid = attack_service.launch(req.mode, req.target, req.channel)
    return {"status": "started", "pid": pid}


@router.get("/status")
def nic_status():
    return {
        "mode": settings.ZEUSNET_MODE,
        "active_attacks": attack_service.status(),
    }
