"""MapIntelligence agent.

Generates map overlays from processed signal events and exposes a minimal
GeoJSON feature collector for the UI heat-map.
"""

import logging


logger = logging.getLogger("zeusnet.map_intel")


class MapIntelligence:
    """Produce GeoJSON heat-map chunks for the UI."""

    def __init__(self) -> None:
        self.features: list[dict] = []

    def process_event(self, data: dict) -> None:
        """Convert a signal event into a GeoJSON feature."""
        lat = data.get("lat") or data.get("latitude")
        lon = data.get("lon") or data.get("longitude")
        if lat is None or lon is None:
            logger.debug("Event missing coordinates: %s", data)
            return

        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                k: v
                for k, v in data.items()
                if k not in {"lat", "lon", "latitude", "longitude"}
            },
        }
        self.features.append(feature)

    def start(self) -> None:
        """Initialize data structures or background tasks."""
        logger.info("MapIntelligence started")
