from sqlalchemy import Column, DateTime, Integer, String
from datetime import datetime
from backend.db import Base


class WiFiScan(Base):
    __tablename__ = "wifi_scans"

    id = Column(Integer, primary_key=True, index=True)
    ssid = Column(String)
    bssid = Column(String)
    rssi = Column(Integer)
    auth = Column(String)
    channel = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ssid": self.ssid,
            "bssid": self.bssid,
            "rssi": self.rssi,
            "auth": self.auth,
            "channel": self.channel,
            "timestamp": self.timestamp,
        }


class DeviceSeen(Base):
    __tablename__ = "device_seen"

    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    vendor = Column(String, nullable=True)
    ssid = Column(String, nullable=True)
    signal_strength = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mac": self.mac,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "vendor": self.vendor,
            "ssid": self.ssid,
            "signal_strength": self.signal_strength,
        }


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, unique=True, index=True)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mac": self.mac,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "message": self.message,
            "created_at": self.created_at,
        }
