"""MapIntelligence agent.

Generates map overlays from processed signal events. This is currently a
placeholder that exposes the expected interface only.
"""


from collections import deque
from typing import Deque


class MapIntelligence:
    """Produce GeoJSON heat-map chunks for the UI."""

    def __init__(self, history_size: int = 100) -> None:
        self.history_size = history_size
        self._recent: Deque[dict] = deque(maxlen=history_size)

    def process_event(self, data: dict) -> dict:
        """Translate a signal event into a GeoJSON Feature.

        Parameters
        ----------
        data: dict
            Event data containing ``lat`` and ``lon`` keys either at the top
            level or under ``payload``.

        Returns
        -------
        dict
            GeoJSON Feature representing the event.
        """

        payload = data.get("payload", data)
        lat = payload.get("lat")
        lon = payload.get("lon")
        if lat is None or lon is None:
            raise ValueError("Event must include 'lat' and 'lon' coordinates")

        properties = {k: v for k, v in payload.items() if k not in {"lat", "lon"}}
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": properties,
        }
        self._recent.append(feature)
        return feature

    def get_recent_features(self) -> list[dict]:
        """Return the most recently processed GeoJSON features."""

        return list(self._recent)

    def start(self) -> None:
        """Start background processing (stub)."""
        pass
