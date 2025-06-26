"""Attack tab placeholder."""

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class AttackView(Gtk.Box):
    """Simple placeholder for attack controls."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label = Gtk.Label(label="Attack controls go here")
        self.append(label)
