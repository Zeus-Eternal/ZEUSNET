"""SignalWatcher agent.

Processes Wi-Fi scan rows coming from the ESP32 and persists them to the
database. This implementation reuses helpers from ``c2.command_bus``.
"""

from backend.c2.command_bus import SerialCommandBus, store_scan_to_db


class SignalWatcher:
    """Filter and store incoming signal data."""

    def __init__(self, bus: SerialCommandBus | None = None) -> None:
        self.bus = bus or SerialCommandBus()
        self.bus.register_listener(self.handle)

    def handle(self, data: dict) -> None:
        """Persist relevant scan data to the database."""
        store_scan_to_db(data)

    def start(self) -> None:
        """Start listening on the serial bus."""
        self.bus.start()
