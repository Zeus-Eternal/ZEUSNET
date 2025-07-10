import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

from backend.services.api_client import NetworkAPIClient


class NetworkList(Gtk.ScrolledWindow):
    __gsignals__ = {
        "target-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }

    COLS = ["SSID", "RSSI", "BSSID", "Channel", "Encryption", "Signal Quality"]

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        self.table_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(self.table_box)

        self.api_client = NetworkAPIClient()
        self._loading = False

        self._build_headers()

    def _build_headers(self):
        header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        for title in self.COLS:
            lbl = Gtk.Label(label=title)
            lbl.set_margin_top(4)
            lbl.set_margin_bottom(4)
            lbl.set_margin_start(12)
            lbl.set_margin_end(12)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_hexpand(True)
            lbl.get_style_context().add_class("heading")
            header_row.append(lbl)
        self.table_box.append(header_row)
        self.header_row = header_row

    def remove_all(self):
        child = self.table_box.get_first_child()
        if not child:
            return
        child = child.get_next_sibling()
        while child:
            next_child = child.get_next_sibling()
            self.table_box.remove(child)
            child = next_child

    def set_loading_state(self, loading: bool):
        self._loading = loading
        self.remove_all()
        if loading:
            loading_row = Gtk.Label(label="Loading networks…")
            loading_row.set_margin_top(16)
            loading_row.set_margin_bottom(16)
            self.table_box.append(loading_row)

    def load_networks(self, filters: dict) -> None:
        self.set_loading_state(True)

        def _on_success(networks):
            self.set_loading_state(False)
            self.load_data(networks)

        def _on_error(err):
            self.set_loading_state(False)
            self.table_box.append(Gtk.Label(label=f"Failed to load networks: {err}"))

        self.api_client.get_networks_async(filters, _on_success, _on_error)

    def load_data(self, networks):
        self.remove_all()
        if not networks:
            self.table_box.append(Gtk.Label(label="No networks found."))
            return

        try:
            networks = sorted(
                networks, key=lambda n: int(n.get("rssi", -999)), reverse=True
            )
        except Exception:
            pass

        seen = set()
        for n in networks:
            key = (n.get("ssid"), n.get("bssid"), n.get("channel"))
            if key in seen:
                continue
            seen.add(key)

            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            row.set_margin_top(2)
            row.set_margin_bottom(2)
            row.set_hexpand(True)
            # Structured columns (aligned, expand, monospace where useful)
            widgets = [
                Gtk.Label(label=f"{n.get('ssid','—')}", xalign=0),
                Gtk.Label(label=f"{n.get('rssi','—')}", xalign=0),
                Gtk.Label(label=f"{n.get('bssid','—')}", xalign=0),
                Gtk.Label(label=f"{n.get('channel','—')}", xalign=0),
                Gtk.Label(label=f"{n.get('encryption','—')}", xalign=0),
                Gtk.Label(label=f"{n.get('quality','—')}", xalign=0),
            ]
            for idx, widget in enumerate(widgets):
                widget.set_margin_start(12)
                widget.set_margin_end(12)
                widget.set_halign(Gtk.Align.START)
                widget.set_hexpand(True)
                # Set monospace for BSSID for better readability
                if idx == 2:
                    widget.set_name("monospace")  # For styling in your CSS
                row.append(widget)

            row._net_info = n
            click = Gtk.GestureClick()
            click.set_button(0)
            # Accept all click signal args (gesture, n_press, x, y, *user_data)
            click.connect("released", self._on_row_clicked, row)
            row.add_controller(click)

            self.table_box.append(row)

    def _on_row_clicked(self, gesture, n_press, x, y, row):
        # Only fire on double-click (n_press == 2)
        if n_press == 2:
            self.emit("target-selected", row._net_info)
