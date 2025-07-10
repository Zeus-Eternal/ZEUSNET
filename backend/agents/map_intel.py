"""MapIntelligence agent.

This experimental module will eventually generate map overlays from
processed signal events. It currently exists as a placeholder and is not
used in production.
"""


class MapIntelligence:
    """Produce GeoJSON heat-map chunks for the UI."""

    def __init__(self) -> None:
        """Initialize the agent (no-op while experimental)."""
        pass

    def process_event(self, data: dict) -> None:
        """Handle a processed signal event (currently a stub)."""
        # Future: translate events into GeoJSON
        pass

    def start(self) -> None:
        """Start background processing (currently a stub)."""
        pass
