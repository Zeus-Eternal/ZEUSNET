from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

from backend import settings as config

router = APIRouter()


@router.get("/settings")
def get_settings():
    return {
        "mode": config.ZEUSNET_MODE,
        "serial_port": config.SERIAL_PORT,
        "serial_baud": config.SERIAL_BAUD,
    }


class SettingsUpdate(BaseModel):
    mode: str | None = None
    serial_port: str | None = None
    serial_baud: int | None = None


class ModeUpdate(BaseModel):
    mode: str


class SerialPortUpdate(BaseModel):
    port: str


class WatchdogUpdate(BaseModel):
    enabled: bool


watchdog_enabled = False


@router.post("/settings")
def update_settings(data: SettingsUpdate):
    if data.mode:
        config.ZEUSNET_MODE = data.mode
        os.environ["ZEUSNET_MODE"] = data.mode
    if data.serial_port:
        config.SERIAL_PORT = data.serial_port
        os.environ["SERIAL_PORT"] = data.serial_port
    if data.serial_baud:
        config.SERIAL_BAUD = data.serial_baud
        os.environ["SERIAL_BAUD"] = str(data.serial_baud)
    return get_settings()


@router.post("/settings/mode")
def update_mode(payload: ModeUpdate):
    mode = payload.mode.upper()
    if mode not in ["SAFE", "AGGRESSIVE"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    config.ZEUSNET_MODE = mode
    os.environ["ZEUSNET_MODE"] = mode
    return {"status": "ok", "mode": mode}


@router.post("/settings/serial_port")
def set_serial_port(payload: SerialPortUpdate):
    config.SERIAL_PORT = payload.port
    os.environ["SERIAL_PORT"] = payload.port
    return {"status": "ok", "port": payload.port}


@router.post("/settings/watchdog")
def toggle_watchdog(payload: WatchdogUpdate):
    global watchdog_enabled
    watchdog_enabled = payload.enabled
    return {"status": "ok", "watchdog": watchdog_enabled}
