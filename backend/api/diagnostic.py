from fastapi import APIRouter

from backend.c2.command_bus import command_bus

router = APIRouter()


@router.get("/diagnostic")
def diagnostic():
    return {
        "port": command_bus.serial_port,
        "listeners": len(command_bus.listeners),
        "last_in": command_bus.last_in,
        "last_out": command_bus.last_out,
    }
