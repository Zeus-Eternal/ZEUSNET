
import serial
from serial.tools import list_ports
import os
import json
import glob
import time
import serial
import logging
import pyudev
import threading
from pathlib import Path
import glob

try:
    import pyudev
except Exception:  # pyudev not available on Windows/macOS
    pyudev = None
import paho.mqtt.client as mqtt
from serial.serialutil import SerialException
from backend.settings import SERIAL_BAUD, MQTT_BROKER, MQTT_TOPIC

logger = logging.getLogger("command_bus")

PERSIST_FILE = "/tmp/zeusnet_last_serial"  # Can be moved to config dir if needed


class SerialCommandBus:
    CONFIG_DIR = Path.home() / ".config" / "zeusnet"
    PERSIST_FILE = CONFIG_DIR / "last_serial"

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.current_port = None
        self.serial_port = self._find_serial_port()
        self.baud_rate = SERIAL_BAUD
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.listeners = []
        self.last_in: dict | None = None
        self.last_out: dict | None = None

    def _find_serial_port(self) -> str:
        """Locate an appropriate serial port and persist it for future runs."""
        cached = None
        if self.PERSIST_FILE.exists():
            cached = self.PERSIST_FILE.read_text().strip()

        preferred_ids = [("10c4", "ea60"), ("1a86", "7523")]

        # Use pyudev on Linux for vendor/product matching
        if pyudev:
            context = pyudev.Context()
            for device in context.list_devices(subsystem="tty"):
                vid = device.get("ID_VENDOR_ID")
                pid = device.get("ID_MODEL_ID")
                if vid and pid and (vid, pid) in preferred_ids:
                    port = device.device_node
                    self.PERSIST_FILE.write_text(port)
                    return port

        # Fall back to pyserial scanning
        ports = [p.device for p in list_ports.comports()]
        if cached and cached in ports:
            return cached
        if ports:
            self.PERSIST_FILE.write_text(ports[0])
            return ports[0]

        # Ultimate fallback to configured default
        self.PERSIST_FILE.write_text(SERIAL_PORT)
        return SERIAL_PORT

    def start(self):
        logger.info(f"[SerialBus] Starting on {self.serial_port} @ {self.baud_rate}")
        self.read_thread.start()
    def __init__(self, baud_rate=SERIAL_BAUD, backoff_base=2, backoff_limit=60):
        self.baud_rate = baud_rate
        self.ser = None
        self.running = True
        self.lock = threading.Lock()
        self.listeners = []
        self.backoff_base = backoff_base
        self.backoff_limit = backoff_limit

        self.current_port = self._load_last_known_port()

        # Watch for device changes
        self.udev_context = pyudev.Context()
        self.udev_monitor = pyudev.Monitor.from_netlink(self.udev_context)
        self.udev_monitor.filter_by(subsystem='tty')
        self.udev_observer = pyudev.MonitorObserver(self.udev_monitor, self._udev_callback)
        self.udev_observer.start()

        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reconnect_thread.start()

    def _udev_callback(self, action, device):
        logger.info(f"[udev] {action} detected: {device.device_node}")
        if action == 'add' or action == 'remove':
            self._reconnect_now()

    def _reconnect_now(self):
        self.disconnect()
        self._connect()

    def _load_last_known_port(self):
        if os.path.exists(PERSIST_FILE):
            with open(PERSIST_FILE, "r") as f:
                return f.read().strip()
        return None

    def _save_last_known_port(self, port):
        with open(PERSIST_FILE, "w") as f:
            f.write(port)

    def _find_serial_port(self):
        candidates = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        if self.current_port in candidates:
            return self.current_port
        return candidates[0] if candidates else None

    def _connect(self):
        port = self._find_serial_port()
        if not port:
            logger.warning("[SerialBus] No serial port found.")
            return False
        try:
            self.ser = serial.Serial(port, self.baud_rate, timeout=1)
            self.current_port = port
            self._save_last_known_port(port)
            logger.info(f"[SerialBus] Connected to {port}")
            if not self.read_thread.is_alive():
                self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
                self.read_thread.start()
            return True
        except SerialException as e:
            logger.error(f"[SerialBus] Failed to connect to {port}: {e}")
            self.ser = None
            return False

    def _reconnect_loop(self):
        delay = 1
        while self.running:
            if self.ser is None or not self.ser.is_open:
                success = self._connect()
                if not success:
                    logger.debug(f"[SerialBus] Retry in {delay}s...")
                    time.sleep(delay)
                    delay = min(self.backoff_limit, delay * self.backoff_base)
                else:
                    delay = 1  # reset after success
            else:
                time.sleep(2)

    def send(self, opcode: int, payload: dict = None):
        packet = {"opcode": opcode, "payload": payload or {}}
        raw = json.dumps(packet).encode("utf-8") + b"\n"
        self.ser.write(raw)
        self.last_out = packet
        logger.debug(f"[SerialBus] Sent to ESP32: {packet}")

    def read_loop(self):
        while True:
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if not line:
                    continue
                data = json.loads(line)
                self.last_in = data
                logger.debug(f"[SerialBus] Received from ESP32: {data}")
                self.notify_listeners(data)
                
            except Exception as e:
                logger.warning(f"[SerialBus] Read error: {e}")

    def register_listener(self, callback):
        self.listeners.append(callback)

    def notify_listeners(self, data):
        for cb in self.listeners:
            try:
                cb(data)
            except Exception as e:
                logger.warning(f"[SerialBus] Listener exception: {e}")

    def disconnect(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                logger.info("[SerialBus] Closing connection.")
                self.ser.close()
            self.ser = None

    def close(self):
        self.running = False
        self.disconnect()


class MQTTCommandRelay:
    def __init__(self, bus: SerialCommandBus):
        self.bus = bus
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.bus.register_listener(self.forward_to_mqtt)

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"[MQTT] Connected to {MQTT_BROKER}")
        client.subscribe(f"{MQTT_TOPIC}/to_esp")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            opcode = payload.get("opcode")
            data = payload.get("payload")
            self.bus.send(opcode, data)
        except Exception as e:
            logger.warning(f"[MQTT] Message error: {e}")

    def forward_to_mqtt(self, data):
        try:
            self.client.publish(f"{MQTT_TOPIC}/from_esp", json.dumps(data))
        except Exception as e:
            logger.warning(f"[MQTT] Publish failed: {e}")

    def start(self):
        logger.info(f"[MQTT] Starting relay to {MQTT_BROKER}")
        try:
            self.client.connect(MQTT_BROKER)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"[MQTT] Could not connect: {e}")


# Entrypoint for integration
command_bus = SerialCommandBus()
mqtt_relay = MQTTCommandRelay(command_bus)


def start_bus():
    command_bus.start()
    mqtt_relay.start()
