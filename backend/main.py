from fastapi import FastAPI
from backend.api import (
    scan,
    networks,
    devices,
    export,
    alerts,
    command,
    diagnostic,
)
from backend.routes import networks as demo_networks
from backend.c2.command_bus import start_bus

app = FastAPI()

# Routers
app.include_router(scan.router, prefix="/api")
app.include_router(networks.router, prefix="/api")
app.include_router(demo_networks.router)
app.include_router(devices.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(command.router, prefix="/api")
app.include_router(diagnostic.router, prefix="/api")


@app.on_event("startup")
def _startup():
    start_bus()
