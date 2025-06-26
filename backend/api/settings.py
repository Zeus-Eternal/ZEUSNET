from fastapi import APIRouter
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

