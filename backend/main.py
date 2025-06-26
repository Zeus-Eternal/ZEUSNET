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
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import networks as demo_networks
from backend.c2.command_bus import start_bus
from backend.db import init_db

app = FastAPI(
    title="ZeusNet API",
    version="0.1.0",
    description="Secure, Real-Time Network Analysis and Control System",
)

# 👋 Root endpoint for friendly browser access
@app.get("/")
def read_root():
    return {
        "status": "ZeusNet API is online",
        "docs": "/docs",
        "networks": "/api/networks",
        "devices": "/api/devices",
        "alerts": "/api/alerts",
        "scan": "/api/scan",
        "command": "/api/command",
        "export_csv": "/api/export/csv",
    }

# 🌐 Add CORS support for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Mount all routers
app.include_router(scan.router, prefix="/api")
app.include_router(networks.router, prefix="/api")
app.include_router(demo_networks.router)
app.include_router(devices.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(command.router, prefix="/api")
app.include_router(diagnostic.router, prefix="/api")

# 🚀 Background startup tasks
@app.on_event("startup")
def _startup():
    init_db()
    start_bus()
