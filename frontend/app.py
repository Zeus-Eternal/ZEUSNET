"""GTK application setup for ZeusNet."""
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

try:  # Allow running this module directly
    from .views.network_view import NetworkView
    from .views.attack_view import AttackView
    from .views.settings_view import SettingsView
    from .views.dashboard_view import DashboardView
except ImportError:  # pragma: no cover - fallback when executed as script
    import os
    import sys

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)
    from frontend.views.network_view import NetworkView
    from frontend.views.attack_view import AttackView
    from frontend.views.settings_view import SettingsView
    from frontend.views.dashboard_view import DashboardView


class ZeusApp(Gtk.Application):
    """Main GTK application class."""

    def __init__(self) -> None:
        super().__init__(application_id="com.zeusnet.viewer")

    def do_activate(self) -> None:
        win = Gtk.ApplicationWindow(application=self, title="ZeusNet")
        win.set_default_size(1200, 800)

        notebook = Gtk.Notebook()
        notebook.append_page(NetworkView(), Gtk.Label(label="Networks"))
        notebook.append_page(AttackView(), Gtk.Label(label="Attack"))
        notebook.append_page(SettingsView(), Gtk.Label(label="Settings"))
        notebook.append_page(DashboardView(), Gtk.Label(label="Dashboard"))

        win.set_child(notebook)
        win.present()
