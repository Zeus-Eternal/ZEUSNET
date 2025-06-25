from sqlalchemy import Column, Integer, String, DateTime
from backend.db import Base  # ✅ Use your project's Base
from datetime import datetime

class DeviceSeen(Base):
    __tablename__ = "device_seen"

    id = Column(Integer, primary_key=True, index=True)
    mac_address = Column(String, nullable=False, index=True)
    ssid = Column(String, nullable=True)
    signal_strength = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class WiFiScan(Base):
    __tablename__ = "wifi_scans"

    id = Column(Integer, primary_key=True, index=True)
    ssid = Column(String)
    bssid = Column(String)
    rssi = Column(Integer)
    auth = Column(String)
    channel = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, unique=True, index=True)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
