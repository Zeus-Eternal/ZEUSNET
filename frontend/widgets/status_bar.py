"""Status bar widget."""

from gi.repository import Gtk


class StatusBar(Gtk.Statusbar):
    """Simple status bar abstraction."""

    def update(self, message: str) -> None:
        self.push(self.get_context_id("status"), message)
