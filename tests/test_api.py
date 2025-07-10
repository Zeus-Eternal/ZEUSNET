import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Import routers and settings
from backend.api import networks, settings as settings_api, nic, export, scan
from backend.db import init_db
import backend.settings as config


@pytest.fixture(scope="module")
def client():
    """Create TestClient with essential routers."""
    # Ensure tables exist
    init_db()
    app = FastAPI()
    app.include_router(networks.router, prefix="/api")
    app.include_router(settings_api.router, prefix="/api")
    app.include_router(scan.router, prefix="/api")
    app.include_router(export.router, prefix="/api")
    app.include_router(nic.router, prefix="/api")
    with TestClient(app) as c:
        yield c


def test_get_settings(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert {"mode", "serial_port", "serial_baud", "watchdog"} <= data.keys()


def test_get_networks_default_mode(client):
    resp = client.get("/api/networks", params={"limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 2
    if data:
        item = data[0]
        assert "ssid" in item
        assert "rssi" in item
        # SAFE mode should omit aggressive fields
        assert "bssid" not in item


def test_aggressive_mode_updates_network_fields(client):
    resp = client.post("/api/settings", json={"mode": "AGGRESSIVE"})
    assert resp.status_code == 200
    assert resp.json()["mode"] == "AGGRESSIVE"
    assert config.ZEUSNET_MODE == "AGGRESSIVE"

    resp = client.get("/api/networks", params={"limit": 1})
    assert resp.status_code == 200
    items = resp.json()
    assert items
    item = items[0]
    assert {"bssid", "auth", "channel", "timestamp"} <= item.keys()


def test_nic_attack_requires_aggressive_mode(client):
    config.ZEUSNET_MODE = "SAFE"
    resp = client.post(
        "/api/nic/attack",
        json={"mode": "deauth", "target": "AA:BB:CC:DD:EE:FF"},
    )
    assert resp.status_code == 403


def test_nic_attack_launch_and_status(client, monkeypatch):
    config.ZEUSNET_MODE = "AGGRESSIVE"

    class DummyProc:
        def __init__(self, pid=999):
            self.pid = pid

    monkeypatch.setattr(nic.subprocess, "Popen", lambda *a, **k: DummyProc())
    nic.attack_service.active.clear()

    resp = client.post(
        "/api/nic/attack",
        json={"mode": "deauth", "target": "AA:BB:CC:DD:EE:FF"},
    )
    assert resp.status_code == 200
    pid = resp.json()["pid"]
    assert pid == 999

    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_attacks"] == {
        pid: {"mode": "deauth", "target": "AA:BB:CC:DD:EE:FF", "channel": None}
    }


def test_export_csv(client):
    now = datetime.utcnow()
    scan_data = [
        {
            "ssid": "TestNet",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "rssi": -20,
            "auth": "open",
            "channel": 1,
            "timestamp": now.isoformat(),
        }
    ]
    resp = client.post("/api/scan", json=scan_data)
    assert resp.status_code == 200

    params = {
        "from_date": (now - timedelta(minutes=1)).isoformat(),
        "to_date": (now + timedelta(minutes=1)).isoformat(),
    }
    resp = client.get("/api/export/csv", params=params)
    assert resp.status_code == 200
    text = resp.text
    assert "SSID,BSSID,RSSI,Auth,Channel,Timestamp" in text
    assert "TestNet" in text