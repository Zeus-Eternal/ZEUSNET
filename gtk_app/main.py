import asyncio
from gi.repository import Gtk, GLib
import aiohttp

API_URL = "http://localhost:8000/api/networks?limit=50"


class NetworkWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="ZeusNet GTK")
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
        scrolled.add(treeview)
        self.add(scrolled)

        GLib.timeout_add_seconds(5, self.refresh)
        asyncio.get_event_loop().create_task(self.fetch())

    async def fetch(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL) as resp:
                    data = await resp.json()
                    self.liststore.clear()
                    for item in data:
                        self.liststore.append(
                            [item.get("ssid", ""), item.get("rssi", 0)]
                        )
        except Exception as e:
            print("Error fetching networks", e)

    def refresh(self):
        asyncio.get_event_loop().create_task(self.fetch())
        return True


def main():
    loop = asyncio.get_event_loop()
    win = NetworkWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    loop.stop()


if __name__ == "__main__":
    main()
