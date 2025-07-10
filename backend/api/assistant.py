from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    prompt: str


@router.post("/assistant/chat")
def assistant_chat(req: ChatRequest) -> dict:
    """Trivial echo-style AI assistant for demo purposes."""
    return {"response": req.prompt[::-1]}
