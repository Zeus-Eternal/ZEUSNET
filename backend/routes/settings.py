from fastapi import APIRouter, Request, HTTPException
import os
from backend import settings as config

router = APIRouter()


@router.post("/api/settings/mode")
async def update_mode(req: Request):
    body = await req.json()
    mode = body.get("mode", "SAFE").upper()
    if mode not in ["SAFE", "AGGRESSIVE"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    os.environ["ZEUSNET_MODE"] = mode
    config.ZEUSNET_MODE = mode
    return {"status": "ok", "mode": mode}


@router.post("/api/settings/serial_port")
async def set_serial_port(req: Request):
    body = await req.json()
    port = body.get("serial_port") or body.get("port")
    if not port:
        raise HTTPException(status_code=400, detail="Missing port")
    config.set_serial_port(port)
    return {"status": "ok", "port": port}


@router.post("/api/settings/watchdog")
async def toggle_watchdog(req: Request):
    body = await req.json()
    enabled = body.get("watchdog") if "watchdog" in body else body.get("enabled")
    if enabled is None:
        raise HTTPException(status_code=400, detail="Missing enabled flag")
    config.set_watchdog_enabled(bool(enabled))
    return {"status": "ok", "watchdog": config.is_watchdog_enabled()}
