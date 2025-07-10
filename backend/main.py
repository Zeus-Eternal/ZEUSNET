from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

from backend.utils.logging import configure_logging
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
    aireplay,
    forge,
    assistant,
)
from backend.routes import networks as route_networks
from backend.routes import settings as route_settings
from backend.routes import nic as route_nic

from backend.core.agent_manager import agent_manager
from backend.db import init_db

logger = logging.getLogger(__name__)

# 🧠 Load env vars (e.g., ZEUSNET_MODE)
load_dotenv()

# 🚀 FastAPI app
app = FastAPI(
    title="ZeusNet API",
    version="0.1.0",
    description="Secure, Real-Time Network Analysis and Control System",
)

# 🌐 CORS for local UI/dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "forge": "/api/forge/send",
        "assistant": "/api/assistant/chat",
    }


# API Routers (always /api prefix)
app.include_router(scan.router, prefix="/api")
app.include_router(networks.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(command.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")
app.include_router(nic.router, prefix="/api")
app.include_router(diagnostic.router, prefix="/api")
app.include_router(covert_ops_agent.router, prefix="/api")
app.include_router(aireplay.router, prefix="/api")
app.include_router(forge.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")

# Custom SQLAlchemy routes (for legacy/extra DB stuff)
app.include_router(route_networks.router, prefix="/api")
app.include_router(route_settings.router)
app.include_router(route_nic.router)


# Startup: DB and C2 bus
@app.on_event("startup")
def _startup():
    configure_logging()
    logger.info("Starting backend services")
    init_db()
    agent_manager.start_all()
