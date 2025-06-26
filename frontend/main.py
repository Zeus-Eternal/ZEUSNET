#!/usr/bin/env python3
import asyncio
import io
import tempfile
import threading
import logging
from typing import Optional, List, Dict, Any
from serial.tools import list_ports
import gi
import aiohttp
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GTK initialization
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, GdkPixbuf  # noqa: E402

try:
    try:
        gi.require_version("WebKit2", "4.1")
    except ValueError:
        gi.require_version("WebKit2", "4.0")
    from gi.repository import WebKit2  # noqa: E402

    WEBKIT_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    WebKit2 = None
    WEBKIT_AVAILABLE = False

# API endpoints
API_BASE = "http://localhost:8000/api/networks"
CMD_URL = "http://localhost:8000/api/command"
SETTINGS_URL = "http://localhost:8000/api/settings"
ATTACK_URL = "http://localhost:8000/api/nic/attack"

class NetworkWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="ZeusNet")
        self.set_default_size(1000, 800)
        
        # Initialize state
        self.filters = {"ssid": "", "auth": "", "limit": "100"}
        self.current_network_data: List[Dict[str, Any]] = []
        
        # Create main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(self.main_box)
        
        # Create notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)
        self.main_box.append(self.notebook)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        self.status_bar.set_hexpand(True)
        self.main_box.append(self.status_bar)
        
        # Create tabs
        self._create_networks_tab()
        self._create_settings_tab()
        self._create_attack_tab()
        self._create_dashboard_tab()
        if WEBKIT_AVAILABLE:
            self._create_map_tab()
        
        # Initialize async loop
        self._init_async_loop()
        
        # Initial data load
        GLib.idle_add(self._initial_load)

    def _init_async_loop(self):
        """Initialize the async event loop in a separate thread."""
        self.loop = asyncio.new_event_loop()
        threading.Thread(
            target=self.loop.run_forever,
            daemon=True,
            name="AsyncLoopThread"
        ).start()
        
        # Schedule periodic updates
        GLib.timeout_add_seconds(5, self.refresh)

    def _initial_load(self):
        """Initial data loading."""
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        asyncio.run_coroutine_threadsafe(self.fetch_settings(), self.loop)
        return False

    def _create_networks_tab(self):
        """Create the networks tab."""
        # Network list
        self.liststore = Gtk.ListStore(str, str, int, int, str, str)
        treeview = Gtk.TreeView(model=self.liststore)
        treeview.connect("row-activated", self.on_row_activated)
        treeview.set_hexpand(True)
        treeview.set_vexpand(True)
        
        columns = [
            ("SSID", 0),
            ("BSSID", 1),
            ("CH", 2),
            ("RSSI", 3),
            ("AUTH", 4),
            ("TIME", 5)
        ]
        
        for title, idx in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=idx)
            treeview.append_column(column)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(treeview)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        # ensure enough room for many rows
        scrolled.set_min_content_height(400)
        
        # Filter controls
        self.filter_ssid = Gtk.Entry(placeholder_text="SSID")
        self.filter_auth = Gtk.Entry(placeholder_text="Auth")
        self.filter_limit = Gtk.Entry(placeholder_text="Limit", text="100")
        
        btn_apply_filters = Gtk.Button(label="Apply Filters")
        btn_apply_filters.connect("clicked", self.on_apply_filters)
        
        filter_box = Gtk.Box(spacing=6)
        filter_box.append(self.filter_ssid)
        filter_box.append(self.filter_auth)
        filter_box.append(self.filter_limit)
        filter_box.append(btn_apply_filters)
        
        # Scan controls
        self.interval_entry = Gtk.Entry(placeholder_text="Interval (ms)")
        btn_set_interval = Gtk.Button(label="Set Interval")
        btn_set_interval.connect("clicked", self.on_set_interval)
        
        self.toggle_scan = Gtk.ToggleButton(label="Scanning", active=True)
        self.toggle_scan.connect("toggled", self.on_toggle_scan)
        
        btn_reboot = Gtk.Button(label="Reboot Device")
        btn_reboot.connect("clicked", self.on_reboot)
        
        scan_controls = Gtk.Box(spacing=6)
        scan_controls.append(self.interval_entry)
        scan_controls.append(btn_set_interval)
        scan_controls.append(self.toggle_scan)
        scan_controls.append(btn_reboot)
        
        # Assemble tab
        network_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        network_page.set_hexpand(True)
        network_page.set_vexpand(True)
        network_page.append(filter_box)
        network_page.append(scrolled)
        network_page.append(scan_controls)
        
        self.notebook.append_page(
            network_page,
            Gtk.Label(label="Networks")
        )

    def _create_settings_tab(self):
        """Create the settings tab."""
        self.mode_label = Gtk.Label(label="Mode: Unknown")
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
        settings_page.set_hexpand(True)
        settings_page.set_vexpand(True)
        
        self.notebook.append_page(
            settings_page,
            Gtk.Label(label="Settings")
        )

    def _create_attack_tab(self):
        """Create the attack tab."""
        self.attack_combo = Gtk.ComboBoxText()
        for mode in ["deauth", "rogue_ap", "pmkid", "swarm"]:
            self.attack_combo.append_text(mode)
        self.attack_combo.set_active(0)
        
        self.attack_target = Gtk.Entry(placeholder_text="Target MAC")
        self.attack_channel = Gtk.Entry(placeholder_text="Channel")
        
        btn_attack = Gtk.Button(label="Launch Attack")
        btn_attack.connect("clicked", self.on_attack)
        
        attack_controls = Gtk.Box(spacing=6)
        attack_controls.append(self.attack_combo)
        attack_controls.append(self.attack_target)
        attack_controls.append(self.attack_channel)
        attack_controls.append(btn_attack)
        
        attack_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        attack_page.append(attack_controls)
        attack_page.set_hexpand(True)
        attack_page.set_vexpand(True)
        
        self.notebook.append_page(
            attack_page,
            Gtk.Label(label="Attack")
        )

    def _create_dashboard_tab(self):
        """Create the dashboard tab."""
        self.chart_image = Gtk.Image()
        self.chart_image.set_hexpand(True)
        self.chart_image.set_vexpand(True)

        dashboard_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        dashboard_page.append(self.chart_image)
        dashboard_page.set_hexpand(True)
        dashboard_page.set_vexpand(True)
        self.notebook.append_page(dashboard_page, Gtk.Label(label="Dashboard"))

    def _create_map_tab(self):
        """Create the map tab (if WebKit is available)."""
        if not WEBKIT_AVAILABLE:
            return
            
        self.webview = WebKit2.WebView()
        self.webview.set_hexpand(True)
        self.webview.set_vexpand(True)

        map_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        map_page.append(self.webview)
        map_page.set_hexpand(True)
        map_page.set_vexpand(True)
        
        self.notebook.append_page(
            map_page,
            Gtk.Label(label="Map")
        )

    # Data fetching methods
    async def fetch(self) -> None:
        """Fetch network data from API."""
        try:
            params = {
                "limit": self.filters["limit"],
                "ssid": self.filters["ssid"],
                "auth": self.filters["auth"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(API_BASE, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.current_network_data = data
                        GLib.idle_add(self.update_store, data)
                        GLib.idle_add(
                            self.update_status,
                            f"Last update: {len(data)} networks"
                        )
                    else:
                        error_msg = f"HTTP Error: {resp.status}"
                        GLib.idle_add(self.update_status, error_msg)
                        logger.error(error_msg)
        except Exception as e:
            error_msg = f"Fetch error: {str(e)}"
            GLib.idle_add(self.update_status, error_msg)
            logger.exception("Error fetching network data")

    async def fetch_settings(self) -> None:
        """Fetch current settings from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(SETTINGS_URL) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_settings, data)
                    else:
                        error_msg = f"Settings HTTP {resp.status}"
                        GLib.idle_add(self.update_status, error_msg)
                        logger.error(error_msg)
        except Exception as e:
            error_msg = f"Settings error: {str(e)}"
            GLib.idle_add(self.update_status, error_msg)
            logger.exception("Error fetching settings")

    # UI update methods
    def update_store(self, data: List[Dict[str, Any]]) -> bool:
        """Update the network list store."""
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
                timestamp
            ])
        
        self.draw_chart(data)
        if WEBKIT_AVAILABLE:
            self.draw_map(data)
        
        return False

    def update_settings(self, data: Dict[str, Any]) -> bool:
        """Update settings UI elements."""
        self.mode_label.set_text(f"Mode: {data.get('mode', 'Unknown')}")
        
        port = data.get("serial_port")
        self.update_ports(port)
        
        return False

    def update_ports(self, current_port: Optional[str]) -> bool:
        """Update the serial ports dropdown."""
        ports = [p.device for p in list_ports.comports()]
        self.port_combo.remove_all()
        
        for port in ports:
            self.port_combo.append_text(port)
        
        if current_port and current_port in ports:
            self.port_combo.set_active(ports.index(current_port))
        elif ports:
            self.port_combo.set_active(0)
        
        return False

    def update_status(self, message: str) -> bool:
        """Update the status bar."""
        self.status_bar.push(0, message)
        return False

    def refresh(self) -> bool:
        """Trigger a refresh of the data."""
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        return True

    # Command methods
    async def send_command(self, opcode: int, payload: Optional[Dict] = None) -> None:
        """Send a command to the API."""
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    CMD_URL,
                    json={
                        "opcode": opcode,
                        "payload": payload or {}
                    }
                )
        except Exception as e:
            error_msg = f"Command error: {str(e)}"
            GLib.idle_add(self.update_status, error_msg)
            logger.exception("Error sending command")

    # Event handlers
    def on_set_interval(self, button: Gtk.Button) -> None:
        """Handle set interval button click."""
        try:
            interval = int(self.interval_entry.get_text())
            if interval <= 0:
                raise ValueError("Interval must be positive")
                
            asyncio.run_coroutine_threadsafe(
                self.send_command(1, {"interval": interval}),
                self.loop
            )
            self.update_status(f"Scan interval set to {interval}ms")
        except ValueError as e:
            self.update_status(f"Invalid interval: {str(e)}")

    def on_toggle_scan(self, button: Gtk.ToggleButton) -> None:
        """Handle scan toggle button click."""
        state = button.get_active()
        asyncio.run_coroutine_threadsafe(
            self.send_command(1, {"scanning": state}),
            self.loop
        )
        self.update_status(f"Scanning {'enabled' if state else 'disabled'}")

    def on_reboot(self, button: Gtk.Button) -> None:
        """Handle reboot button click."""
        asyncio.run_coroutine_threadsafe(
            self.send_command(32),
            self.loop
        )
        self.update_status("Reboot command sent")

    def on_toggle_mode(self, button: Gtk.Button) -> None:
        """Handle mode toggle button click."""
        current_text = self.mode_label.get_text()
        new_mode = "AGGRESSIVE" if "SAFE" in current_text else "SAFE"
        
        asyncio.run_coroutine_threadsafe(
            self.set_mode(new_mode),
            self.loop
        )

    async def set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SETTINGS_URL,
                    json={"mode": mode}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_settings, data)
                        GLib.idle_add(
                            self.update_status,
                            f"Mode set to {mode}"
                        )
                    else:
                        error_msg = f"Mode HTTP {resp.status}"
                        GLib.idle_add(self.update_status, error_msg)
                        logger.error(error_msg)
        except Exception as e:
            error_msg = f"Mode error: {str(e)}"
            GLib.idle_add(self.update_status, error_msg)
            logger.exception("Error setting mode")

    def on_port_selected(self, combo: Gtk.ComboBoxText) -> None:
        """Handle port selection change."""
        port = combo.get_active_text()
        if port:
            asyncio.run_coroutine_threadsafe(
                self.set_port(port),
                self.loop
            )

    async def set_port(self, port: str) -> None:
        """Set the serial port."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SETTINGS_URL,
                    json={"serial_port": port}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        GLib.idle_add(self.update_settings, data)
                        GLib.idle_add(
                            self.update_status,
                            f"Port set to {port}"
                        )
                    else:
                        error_msg = f"Port HTTP {resp.status}"
                        GLib.idle_add(self.update_status, error_msg)
                        logger.error(error_msg)
        except Exception as e:
            error_msg = f"Port error: {str(e)}"
            GLib.idle_add(self.update_status, error_msg)
            logger.exception("Error setting port")

    def on_attack(self, button: Gtk.Button) -> None:
        """Handle attack button click."""
        mode = self.attack_combo.get_active_text()
        target = self.attack_target.get_text()
        channel = self.attack_channel.get_text()
        
        asyncio.run_coroutine_threadsafe(
            self.launch_attack(mode, target, channel),
            self.loop
        )

    async def launch_attack(self, mode: str, target: str, channel: str) -> None:
        """Launch an attack."""
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
                        GLib.idle_add(
                            self.update_status,
                            f"Attack {mode} started"
                        )
                    else:
                        detail = await resp.text()
                        error_msg = f"Attack HTTP {resp.status}: {detail}"
                        GLib.idle_add(self.update_status, error_msg)
                        logger.error(error_msg)
        except Exception as e:
            error_msg = f"Attack error: {str(e)}"
            GLib.idle_add(self.update_status, error_msg)
            logger.exception("Error launching attack")

    def on_row_activated(self, treeview: Gtk.TreeView, path, column) -> None:
        """Handle network row activation."""
        model = treeview.get_model()
        row = model[path]
        bssid = row[1]
        self.attack_target.set_text(bssid)
        self.update_status(f"Selected network: {bssid}")

    def on_apply_filters(self, button: Gtk.Button) -> None:
        """Handle apply filters button click."""
        self.filters["ssid"] = self.filter_ssid.get_text()
        self.filters["auth"] = self.filter_auth.get_text()
        
        try:
            limit = int(self.filter_limit.get_text())
            if limit <= 0:
                raise ValueError("Limit must be positive")
            self.filters["limit"] = str(limit)
        except ValueError:
            self.filters["limit"] = "100"
            self.filter_limit.set_text("100")
        
        asyncio.run_coroutine_threadsafe(self.fetch(), self.loop)
        self.update_status("Filters applied")

    # Visualization methods
    def draw_chart(self, data: List[Dict[str, Any]]) -> None:
        """Draw the RSSI chart."""
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

    def draw_map(self, data: List[Dict[str, Any]]) -> None:
        """Draw the network map (if WebKit is available)."""
        if not WEBKIT_AVAILABLE or not data:
            return
            
        try:
            import folium
            
            # Create map centered on first network or default location
            first_network = data[0]
            lat = first_network.get('latitude', 42.3)
            lon = first_network.get('longitude', -83.1)
            
            fmap = folium.Map(
                location=[lat, lon],
                zoom_start=13,
                tiles='OpenStreetMap'
            )
            
            # Add markers for networks
            for network in data[:20]:  # Limit to 20 for performance
                lat = network.get('latitude', lat)
                lon = network.get('longitude', lon)
                ssid = network.get('ssid', 'Unknown')
                rssi = network.get('rssi', 0)
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5 + (-rssi / 20),  # Bigger for stronger signals
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=f"{ssid} ({rssi} dBm)"
                ).add_to(fmap)
            
            # Save to temp file and load in WebView
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
                fmap.save(tmp.name)
                self.webview.load_uri(f"file://{tmp.name}")
        except ImportError:
            logger.warning("Folium not installed - map disabled")
        except Exception as e:
            logger.exception("Error drawing map")
            self.update_status(f"Map error: {str(e)}")


class ZeusApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.zeusnet.viewer")
        
    def do_activate(self) -> None:
        """Application activation handler."""
        win = NetworkWindow(self)
        win.present()


def main() -> None:
    """Main entry point."""
    app = ZeusApp()
    exit_status = app.run()
    raise SystemExit(exit_status)


if __name__ == "__main__":
    main()
