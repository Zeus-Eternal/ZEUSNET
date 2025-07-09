from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routes import aireplay

# 🔧 Load environment variables (e.g., ZEUSNET_MODE)
load_dotenv()

# 🧠 ZeusNet modules
from backend.api import (
    scan,
    networks,
    devices,
    export,
    alerts,
    command,
    settings as settings_api,
    nic,
    diagnostic,
    covert_ops_agent,
)
from backend.routes import networks as demo_networks
from backend.routes import settings as settings_route
from backend.routes import nic as nic_route

from backend.c2.command_bus import start_bus
from backend.db import init_db

# 🧠 Create the FastAPI app
app = FastAPI(
    title="ZeusNet API",
    version="0.1.0",
    description="Secure, Real-Time Network Analysis and Control System",
)

# 🌐 CORS for local frontend access (e.g., Tauri/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📡 Friendly root endpoint
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
        "mode": "/api/settings/mode",
    }

# 🔌 API Routers (All organized under /api/*)
app.include_router(scan.router, prefix="/api")
app.include_router(networks.router, prefix="/api")
app.include_router(demo_networks.router)  # demo route fallback
app.include_router(devices.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(command.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")
app.include_router(nic.router, prefix="/api")
app.include_router(diagnostic.router, prefix="/api")
app.include_router(covert_ops_agent.router, prefix="/api")
app.include_router(aireplay.router, prefix="/api")

# 🛠 New settings and NIC routes (mode toggling, watchdog, serial config)
app.include_router(settings_route.router)
app.include_router(nic_route.router)

# 🚀 Startup Tasks: Init DB and Command Bus
@app.on_event("startup")
def _startup():
    init_db()
    start_bus()
