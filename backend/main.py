from fastapi import FastAPI
from backend.api import scan, networks, devices, export
from backend.alerts import anomaly, rogue_ap, mac_tracker

app = FastAPI()

# Routers
app.include_router(scan.router, prefix="/api")
app.include_router(networks.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(export.router, prefix="/api")
