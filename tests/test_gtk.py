import pytest

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from frontend.widgets.network_list import NetworkList
except Exception as e:  # skip if GTK not available
    gi = None


def test_network_list_loading_state():
    pytest.importorskip('gi')
    nl = NetworkList()
    nl.set_loading_state(True)
    assert nl._loading is True
