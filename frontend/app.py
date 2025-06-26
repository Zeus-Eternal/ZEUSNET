"""GTK application setup for ZeusNet."""

from gi.repository import Gtk

from .views.network_view import NetworkView
from .views.attack_view import AttackView
from .views.settings_view import SettingsView
from .views.dashboard_view import DashboardView


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
