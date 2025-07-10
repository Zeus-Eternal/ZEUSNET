"""GTK application setup for ZeusNet."""

import gi

gi.require_version("Gtk", "4.0")
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
        # The main window instance is created here.
        if not hasattr(self, "window") or self.window is None:
            self.window = ZeusAppWindow(application=self)
        self.window.present()


class ZeusAppWindow(Gtk.ApplicationWindow):
    """Main Application Window with tab control and attack glue."""

    def __init__(self, application):
        super().__init__(application=application, title="ZeusNet")
        self.set_default_size(1200, 800)

        # --- Tab setup ---
        self.notebook = Gtk.Notebook()
        self.network_view = NetworkView(parent_controller=self)
        self.attack_view = AttackView()
        self.settings_view = SettingsView()
        self.dashboard_view = DashboardView()

        self._attack_tab_index = 1  # Maintain this index if tab order changes!

        self.notebook.append_page(self.network_view, Gtk.Label(label="Networks"))
        self.notebook.append_page(self.attack_view, Gtk.Label(label="Attack"))
        self.notebook.append_page(self.settings_view, Gtk.Label(label="Settings"))
        self.notebook.append_page(self.dashboard_view, Gtk.Label(label="Dashboard"))

        self.set_child(self.notebook)

    def switch_to_attack_tab(self, net_info):
        """
        Switch to Attack tab and prefill attack fields from net_info.
        Called when double-click event from network view fires.
        """
        self.notebook.set_current_page(self._attack_tab_index)
        if hasattr(self.attack_view, "prefill_target"):
            self.attack_view.prefill_target(net_info)
