from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ForgePacket(BaseModel):
    frame_type: str
    payload: str


@router.post("/forge/send")
def forge_send(packet: ForgePacket) -> dict:
    """Accept a crafted packet and echo a simple status."""
    return {
        "status": "sent",
        "frame_type": packet.frame_type,
        "length": len(packet.payload),
    }
