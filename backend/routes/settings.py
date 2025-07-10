from fastapi import APIRouter, Request, HTTPException
import os

router = APIRouter()


@router.post("/api/settings/mode")
async def update_mode(req: Request):
    body = await req.json()
    mode = body.get("mode", "SAFE").upper()
    if mode not in ["SAFE", "AGGRESSIVE"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    os.environ["ZEUSNET_MODE"] = mode
    return {"status": "ok", "mode": mode}


serial_port = None  # Make this global or store in app state


@router.post("/api/settings/serial_port")
async def set_serial_port(req: Request):
    global serial_port
    body = await req.json()
    port = body.get("port")
    if not port:
        raise HTTPException(status_code=400, detail="Missing port")
    serial_port = port
    return {"status": "ok", "port": port}


watchdog_enabled = False


@router.post("/api/settings/watchdog")
async def toggle_watchdog(req: Request):
    global watchdog_enabled
    body = await req.json()
    if "enabled" not in body:
        raise HTTPException(status_code=400, detail="Missing enabled flag")
    enabled = bool(body.get("enabled", False))
    watchdog_enabled = enabled
    return {"status": "ok", "watchdog": watchdog_enabled}
