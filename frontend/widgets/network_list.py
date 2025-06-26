"""Network list widget."""

from gi.repository import Gtk

from ..services.api_client import NetworkAPIClient


class NetworkList(Gtk.ScrolledWindow):
    """Simple network list using a Gtk.ListBox."""

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.list_box = Gtk.ListBox()
        self.set_child(self.list_box)
        self.api_client = NetworkAPIClient()

    def load_networks(self, filters: dict) -> None:
        """Load networks asynchronously and populate the list."""
        # This is a stub; real implementation would be async.
        self.list_box.remove_all()
        item = Gtk.Label(label=f"Loaded networks with filters: {filters}")
        self.list_box.append(item)
