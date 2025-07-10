import logging
from typing import List

from backend.c2.command_bus import command_bus
from backend.agents.zeus_relay import ZeusRelay
from backend.agents.signal_watcher import SignalWatcher
from backend.agents.map_intel import MapIntelligence
from backend.agents.anomaly_guard import AnomalyGuard
from backend.agents.command_hub import CommandHub

logger = logging.getLogger("agent_manager")


class AgentManager:
    """Simple container that owns and starts ZeusNet agents."""

    def __init__(self) -> None:
        self.agents: List[object] = []

    def register(self, agent: object) -> None:
        """Register an agent instance."""
        self.agents.append(agent)

    def start_all(self) -> None:
        """Start each agent if it exposes a ``start`` method."""
        for agent in self.agents:
            start_fn = getattr(agent, "start", None)
            if callable(start_fn):
                try:
                    start_fn()
                    logger.info("Started %s", agent.__class__.__name__)
                except Exception as exc:
                    logger.error("Failed to start %s: %s", agent.__class__.__name__, exc)

    def stop_all(self) -> None:
        """Stop agents that expose a ``stop`` method."""
        for agent in self.agents:
            stop_fn = getattr(agent, "stop", None)
            if callable(stop_fn):
                try:
                    stop_fn()
                    logger.info("Stopped %s", agent.__class__.__name__)
                except Exception as exc:
                    logger.error("Failed to stop %s: %s", agent.__class__.__name__, exc)


def create_default_manager() -> AgentManager:
    """Instantiate the built-in ZeusNet agents with the shared command bus."""
    bus = command_bus

    manager = AgentManager()
    manager.register(ZeusRelay(bus))
    manager.register(SignalWatcher(bus))
    manager.register(MapIntelligence())
    manager.register(AnomalyGuard())
    manager.register(CommandHub())
    return manager


# Export default manager instance
agent_manager = create_default_manager()
