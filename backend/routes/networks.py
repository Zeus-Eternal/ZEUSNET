from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.networks import get_networks as fetch_networks
from backend.db import get_db

router = APIRouter()


@router.get("/networks")
async def get_networks(limit: int = 50, db: Session = Depends(get_db)):
    """Return Wi-Fi networks from the database service."""
    return fetch_networks(limit=limit, db=db)
