import asyncio
import gi
import aiohttp

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
API_URL = "http://localhost:8000/api/networks?limit=50"


class NetworkWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="ZeusNet GTK")
        self.set_default_size(400, 300)

        self.liststore = Gtk.ListStore(str, int)
        treeview = Gtk.TreeView(model=self.liststore)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("SSID", renderer_text, text=0)
        treeview.append_column(column_text)
        renderer_rssi = Gtk.CellRendererText()
        column_rssi = Gtk.TreeViewColumn("RSSI", renderer_rssi, text=1)
        treeview.append_column(column_rssi)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(treeview)
        self.set_child(scrolled)

        GLib.timeout_add_seconds(5, self.refresh)

        # First fetch on load
        asyncio.get_event_loop().create_task(self.fetch())

    async def fetch(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.liststore.clear()
                        for item in data:
                            self.liststore.append(
                                [item.get("ssid", "Unknown"), item.get("rssi", 0)]
                            )
                    else:
                        print(f"HTTP Error: {resp.status}")
        except Exception as e:
            print("Error fetching networks:", e)

    def refresh(self):
        asyncio.get_event_loop().create_task(self.fetch())
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
