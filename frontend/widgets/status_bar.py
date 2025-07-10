"""Status bar widget."""

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402


class StatusBar(Gtk.Statusbar):
    """Simple status bar abstraction."""

    def update(self, message: str) -> None:
        self.push(self.get_context_id("status"), message)
