import asyncio
import threading
import gi
import aiohttp

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
API_URL = "http://localhost:8000/api/networks?limit=100"
CMD_URL = "http://localhost:8000/api/command"
SETTINGS_URL = "http://localhost:8000/api/settings"
ATTACK_URL = "http://localhost:8000/api/nic/attack"


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

        # --- Scan controls ---
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

        # --- Settings controls ---
        self.mode_label = Gtk.Label(label="Mode: ?")
        btn_mode = Gtk.Button(label="Toggle Mode")
        btn_mode.connect("clicked", self.on_toggle_mode)

        self.port_entry = Gtk.Entry()
        self.port_entry.set_placeholder_text("Serial Port")
        btn_port = Gtk.Button(label="Save Port")
        btn_port.connect("clicked", self.on_set_port)

        settings_box = Gtk.Box(spacing=6)
        settings_box.append(self.mode_label)
        settings_box.append(btn_mode)
        settings_box.append(self.port_entry)
        settings_box.append(btn_port)

        # --- Attack controls ---
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

        attack_box = Gtk.Box(spacing=6)
        attack_box.append(self.attack_combo)
        attack_box.append(self.attack_target)
        attack_box.append(self.attack_channel)
        attack_box.append(btn_attack)
        # Status label showing last update or errors
        self.status_label = Gtk.Label(xalign=0)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.append(settings_box)
        container.append(controls)
        container.append(attack_box)
        container.append(scrolled)
        container.append(self.status_label)
        self.set_child(container)

        # Dedicated asyncio loop in a background thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        GLib.timeout_add_seconds(5, self.refresh)

        # First fetch on load
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        asyncio.run_coroutine_threadsafe(self.fetch_settings(), self.loop)

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

    async def fetch_settings(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(SETTINGS_URL) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_settings, data)
                    else:
                        GLib.idle_add(self.update_status, f"Settings HTTP {resp.status}")
        except Exception as e:
            GLib.idle_add(self.update_status, f"Settings error: {e}")

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

    def update_settings(self, data: dict):
        """Update mode label and port entry from fetched settings."""
        self.mode_label.set_text(f"Mode: {data.get('mode', '?')}")
        port = data.get('serial_port')
        if port:
            self.port_entry.set_text(port)
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

    def on_set_port(self, _button):
        port = self.port_entry.get_text()
        asyncio.run_coroutine_threadsafe(self.set_port(port), self.loop)

    async def set_port(self, port: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(SETTINGS_URL, json={"serial_port": port}) as resp:
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
        asyncio.run_coroutine_threadsafe(self.launch_attack(mode, target, channel), self.loop)

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
                        GLib.idle_add(self.update_status, f"Attack HTTP {resp.status}: {detail}")
        except Exception as e:
            GLib.idle_add(self.update_status, f"Attack error: {e}")


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
