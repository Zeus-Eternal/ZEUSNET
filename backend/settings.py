import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Persistent config storage (~/.config/zeusnet/settings.json)
CONFIG_DIR = Path.home() / ".config" / "zeusnet"
CONFIG_FILE = CONFIG_DIR / "settings.json"


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg))


_config = _load_config()

if "serial_port" not in _config:
    _config["serial_port"] = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
if "watchdog_enabled" not in _config:
    _config["watchdog_enabled"] = False

_save_config(_config)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///zeusnet.db")
ZEUSNET_MODE = os.getenv("ZEUSNET_MODE", "SAFE")

# Serial and MQTT defaults for command bus
SERIAL_PORT = _config.get("serial_port", "/dev/ttyUSB0")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "115200"))
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "zeusnet")
RETRY_LIMIT = int(os.getenv("RETRY_LIMIT", "3"))


def get_serial_port() -> str:
    """Return the persisted serial port setting."""
    return _config.get("serial_port", SERIAL_PORT)


def set_serial_port(port: str) -> None:
    """Persist a new serial port value."""
    global SERIAL_PORT
    SERIAL_PORT = port
    _config["serial_port"] = port
    _save_config(_config)


def is_watchdog_enabled() -> bool:
    """Return whether the watchdog is enabled."""
    return bool(_config.get("watchdog_enabled", False))


def set_watchdog_enabled(enabled: bool) -> None:
    """Persist the watchdog enabled state."""
    _config["watchdog_enabled"] = bool(enabled)
    _save_config(_config)
