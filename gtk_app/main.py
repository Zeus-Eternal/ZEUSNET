import asyncio
import threading
import gi
import aiohttp

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
API_URL = "http://localhost:8000/api/networks?limit=50"
CMD_URL = "http://localhost:8000/api/command"


class NetworkWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="ZeusNet GTK")
        self.set_default_size(600, 400)

        # Store: SSID, BSSID, Channel, RSSI, Auth, Time
        self.liststore = Gtk.ListStore(str, str, int, int, str, str)
        treeview = Gtk.TreeView(model=self.liststore)

        columns = [
            ("SSID", 0),
            ("BSSID", 1),
            ("CH", 2),
            ("RSSI", 3),
            ("AUTH", 4),
            ("TIME", 5),
        ]
        for title, idx in columns:
            renderer = Gtk.CellRendererText()
            treeview.append_column(Gtk.TreeViewColumn(title, renderer, text=idx))

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(treeview)

        # Controls
        self.interval_entry = Gtk.Entry()
        self.interval_entry.set_placeholder_text("Interval ms")
        btn_set = Gtk.Button(label="Apply")
        btn_set.connect("clicked", self.on_set_interval)

        self.toggle_scan = Gtk.ToggleButton(label="Scanning")
        self.toggle_scan.set_active(True)
        self.toggle_scan.connect("toggled", self.on_toggle_scan)

        btn_reboot = Gtk.Button(label="Reboot")
        btn_reboot.connect("clicked", self.on_reboot)

        controls = Gtk.Box(spacing=6)
        controls.append(self.interval_entry)
        controls.append(btn_set)
        controls.append(self.toggle_scan)
        controls.append(btn_reboot)
        # Status label showing last update or errors
        self.status_label = Gtk.Label(xalign=0)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.append(controls)
        container.append(scrolled)
        container.append(self.status_label)
        self.set_child(container)

        # Dedicated asyncio loop in a background thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        GLib.timeout_add_seconds(5, self.refresh)

        # First fetch on load
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)

    async def fetch(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_store, data)
                        GLib.idle_add(
                            self.update_status,
                            f"Last update: {len(data)} networks",
                        )
                    else:
                        GLib.idle_add(
                            self.update_status,
                            f"HTTP Error: {resp.status}",
                        )
        except Exception as e:
            GLib.idle_add(self.update_status, f"Error: {e}")

    def update_store(self, data):
        """Update Gtk.ListStore from a background thread."""
        self.liststore.clear()
        for item in data:
            timestamp = item.get("timestamp", "")
            if isinstance(timestamp, str):
                timestamp = timestamp.replace("T", " ").split(".")[0]
            self.liststore.append([
                item.get("ssid", "Unknown"),
                item.get("bssid", "N/A"),
                item.get("channel", 0),
                item.get("rssi", 0),
                item.get("auth", ""),
                timestamp,
            ])
        return False

    def update_status(self, text: str):
        """Update status label safely from any thread."""
        self.status_label.set_text(text)
        return False

    def refresh(self):
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        return True

    async def send_command(self, opcode: int, payload: dict | None = None):
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(CMD_URL, json={"opcode": opcode, "payload": payload or {}})
        except Exception as e:
            GLib.idle_add(self.update_status, f"Cmd error: {e}")

    def on_set_interval(self, _button):
        try:
            value = int(self.interval_entry.get_text())
        except ValueError:
            self.update_status("Invalid interval")
            return
        asyncio.run_coroutine_threadsafe(
            self.send_command(1, {"interval": value}), self.loop
        )

    def on_toggle_scan(self, button):
        state = button.get_active()
        asyncio.run_coroutine_threadsafe(
            self.send_command(1, {"scanning": state}), self.loop
        )

    def on_reboot(self, _button):
        asyncio.run_coroutine_threadsafe(self.send_command(32), self.loop)


class ZeusApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.zeusnet.viewer")

    def do_activate(self, *args):
        win = NetworkWindow(self)
        win.present()


def main():
    app = ZeusApp()
    app.run()


if __name__ == "__main__":
    main()
