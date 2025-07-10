import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.db import Base, get_db
from backend.models import Device, WiFiScan


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestingSessionLocal() as db:
        db.add_all([
            WiFiScan(ssid="TestNet", bssid="aa:bb:cc:dd:ee:ff", rssi=-40, auth="WPA2", channel=6),
            WiFiScan(ssid="Guest", bssid="11:22:33:44:55:66", rssi=-50, auth="Open", channel=1),
        ])
        db.add(Device(mac="aa:bb:cc:dd:ee:ff", first_seen=datetime.utcnow(), last_seen=datetime.utcnow()))
        db.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_get_networks(client):
    resp = client.get("/api/networks")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(n["ssid"] == "TestNet" for n in data)


def test_get_devices(client):
    resp = client.get("/api/devices")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["mac"] == "aa:bb:cc:dd:ee:ff"


def test_nic_attack(monkeypatch, client):
    from backend import settings
    from backend.api import nic

    monkeypatch.setattr(settings, "ZEUSNET_MODE", "AGGRESSIVE")

    class DummyProc:
        pid = 42

        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(nic.subprocess, "Popen", lambda cmd: DummyProc())

    resp = client.post("/api/nic/attack", json={"mode": "rogue_ap"})
    assert resp.status_code == 200
    assert resp.json()["pid"] == 42
