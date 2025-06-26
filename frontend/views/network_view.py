"""Network tab implementation."""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

try:  # Allow running this module directly
    from ..widgets.network_list import NetworkList
    from ..services.api_client import NetworkAPIClient
except ImportError:  # pragma: no cover - fallback when executed as script
    import os
    import sys

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)
    if GRANDPARENT_DIR not in sys.path:
        sys.path.insert(0, GRANDPARENT_DIR)
    from frontend.widgets.network_list import NetworkList
    from frontend.services.api_client import NetworkAPIClient


class NetworkView(Gtk.Box):
    """Displays available networks with filter controls."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.api_client = NetworkAPIClient()
        self._setup_ui()

    def _setup_ui(self) -> None:
        filter_box = Gtk.Box(spacing=6)
        self.filter_entry = Gtk.Entry(placeholder_text="Filter SSID")
        filter_btn = Gtk.Button(label="Apply")
        filter_btn.connect("clicked", self.on_apply_filters)
        filter_box.append(self.filter_entry)
        filter_box.append(filter_btn)

        self.network_list = NetworkList()

        self.append(filter_box)
        self.append(self.network_list)

    def on_apply_filters(self, _button: Gtk.Button) -> None:
        """Refresh networks based on filter."""
        filters = {"ssid": self.filter_entry.get_text()}
        self.network_list.load_networks(filters)
