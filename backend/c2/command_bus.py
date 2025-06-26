import serial
from serial.tools import list_ports
import json
import logging
import threading
from pathlib import Path
import glob

try:
    import pyudev
except Exception:  # pyudev not available on Windows/macOS
    pyudev = None
import paho.mqtt.client as mqtt
from backend.settings import SERIAL_PORT, SERIAL_BAUD, MQTT_BROKER, MQTT_TOPIC

logger = logging.getLogger("command_bus")


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
                logger.warning(f"[SerialBus] Error reading serial: {e}")

    def register_listener(self, callback):
        self.listeners.append(callback)

    def notify_listeners(self, data):
        for cb in self.listeners:
            try:
                cb(data)
            except Exception as e:
                logger.warning(f"[SerialBus] Listener error: {e}")


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
            logger.warning(f"[MQTT] Message handling error: {e}")

    def forward_to_mqtt(self, data):
        try:
            self.client.publish(f"{MQTT_TOPIC}/from_esp", json.dumps(data))
        except Exception as e:
            logger.warning(f"[MQTT] Publish failed: {e}")

    def start(self):
        logger.info(f"[MQTT] Starting MQTTCommandRelay to {MQTT_BROKER}")
        try:
            self.client.connect(MQTT_BROKER)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"[MQTT] Could not connect to broker '{MQTT_BROKER}': {e}")
            logger.warning("[MQTT] Relay is offline. Commands will not sync via MQTT.")


# Entrypoint for integration
command_bus = SerialCommandBus()
mqtt_relay = MQTTCommandRelay(command_bus)


def start_bus():
    command_bus.start()
    mqtt_relay.start()
