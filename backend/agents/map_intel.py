"""MapIntelligence agent.

Generates map overlays from processed signal events. This is currently a
placeholder that exposes the expected interface only.
"""


class MapIntelligence:
    """Produce GeoJSON heat-map chunks for the UI."""

    def __init__(self) -> None:
        pass

    def process_event(self, data: dict) -> None:
        """Handle a processed signal event (stub)."""
        # TODO: translate events into GeoJSON
        pass

    def start(self) -> None:
        """Start background processing (stub)."""
        pass
