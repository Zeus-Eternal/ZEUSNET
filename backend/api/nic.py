from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, validator
import subprocess
import os
import logging
from typing import Literal

from backend import settings

logger = logging.getLogger("zeusnet.nic")

router = APIRouter()


class AttackModel(BaseModel):
    mode: str
    target: str | None = None
    channel: int | None = None


class AttackRequest(BaseModel):
    type: Literal["deauth", "probe", "syn_flood"]
    target: str
    iface: str

    @validator("target")
    def validate_target(cls, v, values):
        if values.get("type") == "deauth":
            if not (len(v.split(":")) == 6 and all(len(part) == 2 for part in v.split(":"))):
                raise ValueError("Target must be a valid MAC address for deauth attack.")
        return v


def run_deauth_attack(target: str, iface: str):
    cmd = ["aireplay-ng", "--deauth", "10", "-a", target, iface]
    return _run_command(cmd, "Deauth Attack")


def run_probe_flood(target: str, iface: str):
    cmd = ["python3", "scripts/probe_flood.py", "--target", target, "--iface", iface]
    return _run_command(cmd, "Probe Flood")


def run_syn_flood(target: str, iface: str):
    cmd = ["python3", "scripts/syn_flood.py", "--target", target, "--iface", iface]
    return _run_command(cmd, "SYN Flood")


def _run_command(cmd, label):
    try:
        logger.info(f"[NIC] Running {label}: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        if result.returncode != 0:
            logger.error(f"[NIC] {label} Failed: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"{label} failed: {result.stderr.strip()}")
        return {"status": "success", "output": result.stdout.strip()}
    except subprocess.TimeoutExpired:
        logger.warning(f"[NIC] {label} Timed out")
        raise HTTPException(status_code=500, detail=f"{label} timed out")
    except Exception as e:
        logger.exception(f"[NIC] Error in {label}")
        raise HTTPException(status_code=500, detail=str(e))


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
        if mode == "probe":
            return ["python3", "scripts/probe_flood.py", "--target", target or "00:00:00:00:00:00", "--iface", "wlan0"]
        if mode == "syn_flood":
            return ["python3", "scripts/syn_flood.py", "--target", target or "127.0.0.1", "--iface", "wlan0"]
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


@router.post("/nic/legacy_attack")
async def legacy_attack(request: Request):
    mode = os.environ.get("ZEUSNET_MODE", "SAFE").upper()
    if mode != "AGGRESSIVE":
        raise HTTPException(status_code=403, detail="Attack blocked in SAFE mode")

    data = await request.json()
    attack = AttackRequest(**data)

    if attack.type == "deauth":
        return run_deauth_attack(attack.target, attack.iface)
    if attack.type == "probe":
        return run_probe_flood(attack.target, attack.iface)
    if attack.type == "syn_flood":
        return run_syn_flood(attack.target, attack.iface)
    raise HTTPException(status_code=400, detail="Unsupported attack type")


@router.get("/status")
def nic_status():
    return {
        "mode": settings.ZEUSNET_MODE,
        "active_attacks": attack_service.status(),
    }
