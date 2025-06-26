"""Settings tab placeholder."""

from gi.repository import Gtk


class SettingsView(Gtk.Box):
    """Simple placeholder for settings controls."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label = Gtk.Label(label="Settings go here")
        self.append(label)
