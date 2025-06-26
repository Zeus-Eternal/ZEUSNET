import asyncio
import threading
import gi
import aiohttp

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
API_URL = "http://localhost:8000/api/networks?limit=50"


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

        # Status label showing last update or errors
        self.status_label = Gtk.Label(xalign=0)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.append(scrolled)
        container.append(self.status_label)
        self.set_child(container)

        # Dedicated asyncio loop in a background thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

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

    def refresh(self):
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        return True


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
