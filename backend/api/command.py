from fastapi import APIRouter
from pydantic import BaseModel

from backend.c2.command_bus import command_bus

router = APIRouter()


class CommandModel(BaseModel):
    opcode: int
    payload: dict | None = None


@router.post("/command")
def send_command(cmd: CommandModel):
    command_bus.send(cmd.opcode, cmd.payload)
    return {"status": "sent"}
