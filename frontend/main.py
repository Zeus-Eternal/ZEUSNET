import asyncio
import io
import tempfile
import threading
from serial.tools import list_ports

import gi
import aiohttp
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, GdkPixbuf

try:
    gi.require_version("WebKit2", "4.0")
    from gi.repository import WebKit2
except Exception:  # pragma: no cover - optional dependency
    WebKit2 = None

API_BASE = "http://localhost:8000/api/networks"
CMD_URL = "http://localhost:8000/api/command"
SETTINGS_URL = "http://localhost:8000/api/settings"
ATTACK_URL = "http://localhost:8000/api/nic/attack"


class NetworkWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="ZeusNet")
        self.set_default_size(800, 600)

        self.status_label = Gtk.Label(xalign=0)

        self.notebook = Gtk.Notebook()
        self.set_child(self.notebook)

        # ----- Networks tab -----
        self.filters = {"ssid": "", "auth": "", "limit": "100"}

        self.liststore = Gtk.ListStore(str, str, int, int, str, str)
        treeview = Gtk.TreeView(model=self.liststore)
        treeview.connect("row-activated", self.on_row_activated)
        for title, idx in [
            ("SSID", 0),
            ("BSSID", 1),
            ("CH", 2),
            ("RSSI", 3),
            ("AUTH", 4),
            ("TIME", 5),
        ]:
            renderer = Gtk.CellRendererText()
            treeview.append_column(Gtk.TreeViewColumn(title, renderer, text=idx))

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_child(treeview)

        # filter controls
        self.filter_ssid = Gtk.Entry()
        self.filter_ssid.set_placeholder_text("SSID")
        self.filter_auth = Gtk.Entry()
        self.filter_auth.set_placeholder_text("Auth")
        self.filter_limit = Gtk.Entry()
        self.filter_limit.set_placeholder_text("Limit")
        self.filter_limit.set_text("100")
        btn_apply_filters = Gtk.Button(label="Apply")
        btn_apply_filters.connect("clicked", self.on_apply_filters)

        filter_box = Gtk.Box(spacing=6)
        filter_box.append(self.filter_ssid)
        filter_box.append(self.filter_auth)
        filter_box.append(self.filter_limit)
        filter_box.append(btn_apply_filters)

        self.interval_entry = Gtk.Entry()
        self.interval_entry.set_placeholder_text("Interval ms")
        btn_set = Gtk.Button(label="Apply")
        btn_set.connect("clicked", self.on_set_interval)

        self.toggle_scan = Gtk.ToggleButton(label="Scanning")
        self.toggle_scan.set_active(True)
        self.toggle_scan.connect("toggled", self.on_toggle_scan)

        btn_reboot = Gtk.Button(label="Reboot")
        btn_reboot.connect("clicked", self.on_reboot)

        scan_controls = Gtk.Box(spacing=6)
        scan_controls.append(self.interval_entry)
        scan_controls.append(btn_set)
        scan_controls.append(self.toggle_scan)
        scan_controls.append(btn_reboot)

        network_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        network_page.append(filter_box)
        network_page.append(scrolled)
        network_page.append(scan_controls)
        network_page.append(self.status_label)
        self.notebook.append_page(network_page, Gtk.Label(label="Networks"))

        # ----- Settings tab -----
        self.mode_label = Gtk.Label(label="Mode: ?")
        btn_mode = Gtk.Button(label="Toggle Mode")
        btn_mode.connect("clicked", self.on_toggle_mode)

        self.port_combo = Gtk.ComboBoxText()
        self.port_combo.connect("changed", self.on_port_selected)

        settings_box = Gtk.Box(spacing=6)
        settings_box.append(self.mode_label)
        settings_box.append(btn_mode)
        settings_box.append(self.port_combo)

        settings_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        settings_page.append(settings_box)
        self.notebook.append_page(settings_page, Gtk.Label(label="Settings"))

        # ----- Attack tab -----
        self.attack_combo = Gtk.ComboBoxText()
        for mode in ["deauth", "rogue_ap", "pmkid", "swarm"]:
            self.attack_combo.append_text(mode)
        self.attack_combo.set_active(0)
        self.attack_target = Gtk.Entry()
        self.attack_target.set_placeholder_text("Target MAC")
        self.attack_channel = Gtk.Entry()
        self.attack_channel.set_placeholder_text("Channel")
        btn_attack = Gtk.Button(label="Launch")
        btn_attack.connect("clicked", self.on_attack)

        attack_controls = Gtk.Box(spacing=6)
        attack_controls.append(self.attack_combo)
        attack_controls.append(self.attack_target)
        attack_controls.append(self.attack_channel)
        attack_controls.append(btn_attack)

        attack_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        attack_page.append(attack_controls)
        self.notebook.append_page(attack_page, Gtk.Label(label="Attack"))

        # ----- Dashboard tab -----
        self.chart_image = Gtk.Image()
        dashboard_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        dashboard_page.append(self.chart_image)
        self.notebook.append_page(dashboard_page, Gtk.Label(label="Dashboard"))

        # ----- Map tab -----
        if WebKit2:
            self.webview = WebKit2.WebView()
            map_container = self.webview
        else:
            self.webview = None
            map_container = Gtk.Label(label="WebKit2 not available")

        map_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        map_page.append(map_container)
        self.notebook.append_page(map_page, Gtk.Label(label="Map"))

        # ---- Async loop ----
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        GLib.timeout_add_seconds(5, self.refresh)
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        asyncio.run_coroutine_threadsafe(self.fetch_settings(), self.loop)

    # ----- Data fetchers -----
    async def fetch(self):
        try:
            params = []
            if self.filters["limit"]:
                params.append(f"limit={self.filters['limit']}")
            if self.filters["ssid"]:
                params.append(f"ssid={self.filters['ssid']}")
            if self.filters["auth"]:
                params.append(f"auth={self.filters['auth']}")
            url = API_BASE
            if params:
                url += "?" + "&".join(params)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
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

    async def fetch_settings(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(SETTINGS_URL) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_settings, data)
                    else:
                        GLib.idle_add(
                            self.update_status, f"Settings HTTP {resp.status}"
                        )
        except Exception as e:
            GLib.idle_add(self.update_status, f"Settings error: {e}")

    # ----- UI update helpers -----
    def update_store(self, data):
        self.liststore.clear()
        for item in data:
            timestamp = item.get("timestamp", "")
            if isinstance(timestamp, str):
                timestamp = timestamp.replace("T", " ").split(".")[0]
            self.liststore.append(
                [
                    item.get("ssid", "Unknown"),
                    item.get("bssid", "N/A"),
                    item.get("channel", 0),
                    item.get("rssi", 0),
                    item.get("auth", ""),
                    timestamp,
                ]
            )
        self.draw_chart(data)
        self.draw_map(data)
        return False

    def update_ports(self, current: str | None):
        ports = [p.device for p in list_ports.comports()]
        self.port_combo.remove_all()
        for p in ports:
            self.port_combo.append_text(p)
        if current and current in ports:
            self.port_combo.set_active(ports.index(current))
        elif ports:
            self.port_combo.set_active(0)
        return False

    def update_settings(self, data: dict):
        self.mode_label.set_text(f"Mode: {data.get('mode', '?')}")
        port = data.get("serial_port")
        self.update_ports(port)
        return False

    def update_status(self, text: str):
        self.status_label.set_text(text)
        return False

    def refresh(self):
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        return True

    # ----- Backend communication wrappers -----
    async def send_command(self, opcode: int, payload: dict | None = None):
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    CMD_URL, json={"opcode": opcode, "payload": payload or {}}
                )
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

    def on_toggle_mode(self, _button):
        current = "AGGRESSIVE" if "SAFE" in self.mode_label.get_text() else "SAFE"
        asyncio.run_coroutine_threadsafe(self.set_mode(current), self.loop)

    async def set_mode(self, mode: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(SETTINGS_URL, json={"mode": mode}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_settings, data)
                    else:
                        GLib.idle_add(self.update_status, f"Mode HTTP {resp.status}")
        except Exception as e:
            GLib.idle_add(self.update_status, f"Mode error: {e}")

    def on_port_selected(self, combo):
        port = combo.get_active_text()
        if port:
            asyncio.run_coroutine_threadsafe(self.set_port(port), self.loop)

    async def set_port(self, port: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SETTINGS_URL, json={"serial_port": port}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_settings, data)
                    else:
                        GLib.idle_add(self.update_status, f"Port HTTP {resp.status}")
        except Exception as e:
            GLib.idle_add(self.update_status, f"Port error: {e}")

    def on_attack(self, _button):
        mode = self.attack_combo.get_active_text()
        target = self.attack_target.get_text()
        channel = self.attack_channel.get_text()
        asyncio.run_coroutine_threadsafe(
            self.launch_attack(mode, target, channel), self.loop
        )

    async def launch_attack(self, mode: str, target: str, channel: str):
        payload = {"mode": mode}
        if target:
            payload["target"] = target
        if channel:
            try:
                payload["channel"] = int(channel)
            except ValueError:
                pass
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(ATTACK_URL, json=payload) as resp:
                    if resp.status == 200:
                        GLib.idle_add(self.update_status, "Attack triggered")
                    else:
                        detail = await resp.text()
                        GLib.idle_add(
                            self.update_status,
                            f"Attack HTTP {resp.status}: {detail}",
                        )
        except Exception as e:
            GLib.idle_add(self.update_status, f"Attack error: {e}")

    def on_row_activated(self, tree_view, path, _column):
        model = tree_view.get_model()
        row = model[path]
        bssid = row[1]
        self.attack_target.set_text(bssid)

    def on_apply_filters(self, _button):
        self.filters["ssid"] = self.filter_ssid.get_text()
        self.filters["auth"] = self.filter_auth.get_text()
        try:
            self.filters["limit"] = str(int(self.filter_limit.get_text()))
        except ValueError:
            self.filters["limit"] = "100"
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)

    def draw_chart(self, data: list[dict]):
        if not data:
            return
        top = sorted(data, key=lambda d: d.get("rssi", -100), reverse=True)[:10]
        ssids = [d.get("ssid", "") for d in top]
        rssis = [d.get("rssi", 0) for d in top]

        fig = Figure(figsize=(6, 3))
        ax = fig.add_subplot(111)
        ax.bar(ssids, rssis, color="steelblue")
        ax.set_ylabel("RSSI")
        ax.set_ylim(-100, 0)
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        buf = io.BytesIO()
        FigureCanvasAgg(fig).print_png(buf)
        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        loader.write(buf.getvalue())
        loader.close()
        self.chart_image.set_from_pixbuf(loader.get_pixbuf())

    def draw_map(self, data: list[dict]):
        if not WebKit2:
            return
        import folium

        center = [42.3, -83.1]
        fmap = folium.Map(location=center, zoom_start=13)
        for idx, _ in enumerate(data[:20]):
            lat = center[0] + 0.002 * idx
            lon = center[1]
            folium.CircleMarker(location=[lat, lon], radius=5, color="red").add_to(fmap)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fmap.save(tmp.name)
        self.webview.load_uri(f"file://{tmp.name}")


class ZeusApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.zeusnet.viewer")

    def do_activate(self, _app):
        win = NetworkWindow(self)
        win.present()


def main():
    app = ZeusApp()
    app.run()


if __name__ == "__main__":
    main()
