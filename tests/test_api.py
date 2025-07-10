import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import routers and settings
from backend.api import networks, settings as settings_api, nic, aireplay
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
    app.include_router(nic.router, prefix="/api")
    app.include_router(aireplay.router, prefix="/api")
    aireplay.AIREPLAY_BIN = "/bin/echo"
    with TestClient(app) as c:
        yield c


def test_get_settings(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert {"mode", "serial_port", "serial_baud"} <= data.keys()


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


def test_nic_attack_requires_aggressive(client):
    resp = client.post(
        "/api/nic/attack",
        json={"mode": "deauth", "target": "AA:BB:CC:DD:EE:FF"},
    )
    assert resp.status_code == 403


def test_nic_attack_after_mode_change(client):
    client.post("/api/settings", json={"mode": "AGGRESSIVE"})
    resp = client.post(
        "/api/nic/attack",
        json={"mode": "deauth", "target": "AA:BB:CC:DD:EE:FF"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "started"
    assert "pid" in data


def test_aireplay_deauth_guard(client):
    client.post("/api/settings", json={"mode": "SAFE"})
    resp = client.post(
        "/api/aireplay/deauth",
        params={"target_bssid": "AA:BB:CC:DD:EE:FF"},
    )
    assert resp.status_code == 403


def test_aireplay_deauth_runs(client):
    client.post("/api/settings", json={"mode": "AGGRESSIVE"})
    resp = client.post(
        "/api/aireplay/deauth",
        params={"target_bssid": "AA:BB:CC:DD:EE:FF"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "queued"

