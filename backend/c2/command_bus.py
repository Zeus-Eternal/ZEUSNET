import serial
import json
import logging
import threading
import paho.mqtt.client as mqtt
from backend.settings import SERIAL_PORT, SERIAL_BAUD, MQTT_BROKER, MQTT_TOPIC

logger = logging.getLogger("command_bus")


class SerialCommandBus:
    def __init__(self):
        self.serial_port = SERIAL_PORT
        self.baud_rate = SERIAL_BAUD
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.listeners = []

    def start(self):
        logger.info(f"[SerialBus] Starting on {self.serial_port} @ {self.baud_rate}")
        self.read_thread.start()

    def send(self, opcode: int, payload: dict = None):
        packet = {
            "opcode": opcode,
            "payload": payload or {}
        }
        raw = json.dumps(packet).encode("utf-8") + b"\n"
        self.ser.write(raw)
        logger.debug(f"[SerialBus] Sent to ESP32: {packet}")

    def read_loop(self):
        while True:
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if not line:
                    continue
                data = json.loads(line)
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
