"""CommandHub agent.

Acts as the central intent router for ZeusNet. This stub exposes a simple
``dispatch`` method used by the REST API layer.
"""

from backend.c2.command_bus import command_bus


class CommandHub:
    """Route commands to the SerialCommandBus."""

    def dispatch(self, opcode: int, payload: dict | None = None) -> None:
        """Forward a command to the ESP32 bus."""
        command_bus.send(opcode, payload)
