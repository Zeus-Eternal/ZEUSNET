from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import Device

router = APIRouter()


@router.get("/devices")
def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()
