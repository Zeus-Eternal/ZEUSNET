import os
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AireplayParams(BaseModel):
    target_mac: str
    ap_mac: str
    iface: str
    count: int = 100

@router.post("/api/attack/aireplay")
def run_aireplay(params: AireplayParams):
    mode = os.environ.get("ZEUSNET_MODE", "SAFE")
    if mode == "SAFE":
        raise HTTPException(status_code=403, detail="Blocked in SAFE mode")

    try:
        cmd = [
            "aireplay-ng",
            "--deauth", str(params.count),
            "-a", params.ap_mac,
            "-c", params.target_mac,
            params.iface
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "status": "executed",
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
