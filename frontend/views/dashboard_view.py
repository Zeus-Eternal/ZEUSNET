"""Dashboard tab placeholder."""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class DashboardView(Gtk.Box):
    """Simple placeholder for dashboard graphs."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label = Gtk.Label(label="Dashboard view")
        self.append(label)
