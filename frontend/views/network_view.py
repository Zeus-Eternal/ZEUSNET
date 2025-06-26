"""Network tab implementation."""

from gi.repository import Gtk

from ..widgets.network_list import NetworkList
from ..services.api_client import NetworkAPIClient


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
