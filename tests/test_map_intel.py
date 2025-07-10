import os
import sys

import pytest

# Ensure the backend package is importable when running `pytest` directly.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.agents.map_intel import MapIntelligence


def test_process_event_to_geojson():
    agent = MapIntelligence(history_size=5)
    event = {"payload": {"ssid": "net", "rssi": -45, "lat": 1.0, "lon": 2.0}}
    feature = agent.process_event(event)
    assert feature["type"] == "Feature"
    assert feature["geometry"] == {"type": "Point", "coordinates": [2.0, 1.0]}
    assert feature["properties"]["ssid"] == "net"
    assert agent.get_recent_features() == [feature]


def test_history_rollover():
    agent = MapIntelligence(history_size=2)
    agent.process_event({"payload": {"lat": 0, "lon": 0}})
    second = agent.process_event({"payload": {"lat": 1, "lon": 1}})
    third = agent.process_event({"payload": {"lat": 2, "lon": 2}})

    recent = agent.get_recent_features()
    assert len(recent) == 2
    assert recent[0] == second
    assert recent[1] == third


def test_missing_coords_raises():
    agent = MapIntelligence()
    with pytest.raises(ValueError):
        agent.process_event({"payload": {"lat": 0}})
