import json
import time
import logging
import threading
from pathlib import Path

import serial
from serial.tools import list_ports
from serial.serialutil import SerialException

try:
    import pyudev
except ImportError:
    pyudev = None

import paho.mqtt.client as mqtt
from backend.db import SessionLocal
from backend.models import WiFiScan

from backend.settings import (
    get_serial_port,
    SERIAL_BAUD,
    MQTT_BROKER,
    MQTT_TOPIC,
    RETRY_LIMIT,
)

# ESP32 -> PC opcodes
OPCODE_SCAN_RESULT = 0x10

logger = logging.getLogger("command_bus")


class SerialCommandBus:
    """Manage ESP32 serial connection with hotplug and persistence."""

    CONFIG_DIR = Path.home() / ".config" / "zeusnet"
    PERSIST_FILE = CONFIG_DIR / "last_serial"

    def __init__(
        self,
        baud_rate: int = SERIAL_BAUD,
        backoff_base: int = 2,
        backoff_limit: int = 60,
        error_limit: int = 3,
    ):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.baud_rate = baud_rate
        self.backoff_base = backoff_base
        self.backoff_limit = backoff_limit
        self.error_limit = error_limit
        self._error_count = 0

        self.ser: serial.Serial | None = None
        self.lock = threading.Lock()
        self.running = True

        self.listeners: list = []
        self.last_in: dict | None = None
        self.last_out: dict | None = None

        self.current_port = self._load_last_known_port()

        if pyudev:
            self.udev_context = pyudev.Context()
            self.udev_monitor = pyudev.Monitor.from_netlink(self.udev_context)
            self.udev_monitor.filter_by(subsystem="tty")
            self.udev_observer = pyudev.MonitorObserver(
                self.udev_monitor, self._udev_callback
            )
            self.udev_observer.start()
        else:
            self.udev_observer = None

        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reconnect_thread = threading.Thread(
            target=self._reconnect_loop, daemon=True
        )

    def _load_last_known_port(self) -> str | None:
        if self.PERSIST_FILE.exists():
            return self.PERSIST_FILE.read_text().strip()
        return None

    def _save_last_known_port(self, port: str) -> None:
        self.PERSIST_FILE.write_text(port)

    def _find_serial_port(self) -> str | None:
        preferred_ids = [("10c4", "ea60"), ("1a86", "7523")]

        if pyudev:
            for device in pyudev.Context().list_devices(subsystem="tty"):
                vid = device.get("ID_VENDOR_ID")
                pid = device.get("ID_MODEL_ID")
                if vid and pid and (vid, pid) in preferred_ids:
                    port = device.device_node
                    self._save_last_known_port(port)
                    return port

        ports = [p.device for p in list_ports.comports()]
        if self.current_port and self.current_port in ports:
            return self.current_port
        if ports:
            self._save_last_known_port(ports[0])
            return ports[0]

        return get_serial_port()

    def _udev_callback(self, action, device):
        logger.info(f"[udev] {action} detected: {device.device_node}")
        if action in ("add", "remove"):
            self._reconnect_now()

    def _reconnect_now(self):
        self.disconnect()
        self._connect()

    def _connect(self) -> bool:
        port = self._find_serial_port()
        if not port:
            logger.warning("[SerialBus] No serial port found.")
            return False
        try:
            self.ser = serial.Serial(port, self.baud_rate, timeout=1)
        except SerialException as e:
            logger.error(f"[SerialBus] Failed to connect to {port}: {e}")
            self.ser = None
            return False

        self.current_port = port
        self._save_last_known_port(port)
        logger.info(f"[SerialBus] Connected to {port}")

        if not self.read_thread.is_alive():
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
        return True

    def _reconnect_loop(self) -> None:
        delay = 1
        while self.running:
            if self.ser is None or not self.ser.is_open:
                success = self._connect()
                if not success:
                    logger.debug(f"[SerialBus] Reconnect retry in {delay}s...")
                    time.sleep(delay)
                    delay = min(self.backoff_limit, delay * self.backoff_base)
                else:
                    delay = 1
            else:
                time.sleep(2)

    def _read_loop(self) -> None:
        while self.running:
            if not self.ser:
                time.sleep(1)
                continue
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if not line:
                    continue
                data = json.loads(line)
                self.last_in = data
                logger.debug(f"[SerialBus] Incoming: {data}")
                self.notify_listeners(data)
                self._error_count = 0
            except Exception as e:
                self._error_count += 1
                logger.warning(f"[SerialBus] Read error: {e}")
                if self._error_count >= self.error_limit:
                    logger.warning("[SerialBus] Too many read errors, reconnecting")
                    self._error_count = 0
                    self._reconnect_now()

    def send(self, opcode: int, payload: dict | None = None) -> None:
        if not self.ser:
            logger.warning("[SerialBus] Cannot send, serial not connected.")
            return
        packet = {"opcode": opcode, "payload": payload or {}}
        raw = json.dumps(packet).encode("utf-8") + b"\n"
        self.ser.write(raw)
        self.last_out = packet
        logger.debug(f"[SerialBus] Sent to ESP32: {packet}")

    def register_listener(self, callback) -> None:
        self.listeners.append(callback)

    def notify_listeners(self, data) -> None:
        for cb in self.listeners:
            try:
                cb(data)
            except Exception as e:
                logger.warning(f"[SerialBus] Listener error: {e}")

    def start(self) -> None:
        logger.info("[SerialBus] Starting")
        self._connect()
        if not self.reconnect_thread.is_alive():
            self.reconnect_thread.start()

    def disconnect(self) -> None:
        with self.lock:
            if self.ser and self.ser.is_open:
                logger.info("[SerialBus] Disconnecting.")
                self.ser.close()
            self.ser = None

    def close(self) -> None:
        self.running = False
        self.disconnect()

    @property
    def serial_port(self) -> str | None:
        return self.current_port


class MQTTCommandRelay:
    def __init__(self, bus: SerialCommandBus):
        self.bus = bus
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.bus.register_listener(self.forward_to_mqtt)

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"[MQTT] Connected to broker: {MQTT_BROKER}")
        client.subscribe(f"{MQTT_TOPIC}/to_esp")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            opcode = payload.get("opcode")
            data = payload.get("payload")
            self.bus.send(opcode, data)
        except Exception as e:
            logger.warning(f"[MQTT] Error parsing message: {e}")

    def forward_to_mqtt(self, data):
        try:
            self.client.publish(f"{MQTT_TOPIC}/from_esp", json.dumps(data))
        except Exception as e:
            logger.warning(f"[MQTT] Failed to publish: {e}")

    def start(self):
        logger.info("[MQTT] Starting MQTT relay...")
        try:
            self.client.connect(MQTT_BROKER)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"[MQTT] Connection failed: {e}")


def store_scan_to_db(data: dict) -> None:
    """Persist incoming scan results to the database."""
    if data.get("opcode") != OPCODE_SCAN_RESULT:
        return
    payload = data.get("payload", {})
    session = SessionLocal()
    try:
        scan = WiFiScan(
            ssid=payload.get("ssid"),
            bssid=payload.get("bssid"),
            rssi=payload.get("rssi"),
            auth=payload.get("auth"),
            channel=payload.get("channel"),
        )
        session.add(scan)
        session.commit()
        logger.debug(f"[DB] Stored scan: {scan.ssid} {scan.bssid}")
    except Exception as e:
        logger.warning(f"[DB] Failed to store scan: {e}")
        session.rollback()
    finally:
        session.close()


# Entrypoint for use
command_bus = SerialCommandBus(error_limit=RETRY_LIMIT)
command_bus.register_listener(store_scan_to_db)
mqtt_relay = MQTTCommandRelay(command_bus)


def start_bus():
    command_bus.start()
    mqtt_relay.start()
