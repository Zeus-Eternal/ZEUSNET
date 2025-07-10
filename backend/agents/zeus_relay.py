"""ZeusRelay agent.

Bridges serial frames from ESP32 nodes to the MQTT broker and vice versa.
This is a thin wrapper around the existing command bus utilities.
"""

from backend.c2.command_bus import SerialCommandBus, MQTTCommandRelay


class ZeusRelay:
    """Bidirectional MQTT <-> Serial relay."""

    def __init__(self, bus: SerialCommandBus | None = None) -> None:
        self.bus = bus or SerialCommandBus()
        self.relay = MQTTCommandRelay(self.bus)

    def start(self) -> None:
        """Start the underlying command bus and MQTT relay."""
        self.bus.start()
        self.relay.start()
