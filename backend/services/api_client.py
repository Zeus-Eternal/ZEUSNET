"""Threaded API client for ZeusNet backend — Production GTK4 Edition.

- No asyncio, no aiohttp, just requests+threads.
- All callbacks are posted safely to GLib/GTK main loop.
"""

import requests
import threading
from gi.repository import GLib
from typing import Any, Callable, Dict, List

class APIError(Exception):
    """Raised when an API request returns an error status."""

# === SETTINGS CLIENT ===

class SettingsAPIClient:
    """Client for application settings endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip("/")

    def fetch_settings(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/settings", timeout=6)
        if resp.status_code != 200:
            raise APIError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_settings_async(self, on_success: Callable[[Dict[str, Any]], None], on_error: Callable[[Exception], None]):
        def _task():
            try:
                data = self.fetch_settings()
                GLib.idle_add(on_success, data)
            except Exception as exc:
                GLib.idle_add(on_error, exc)
        threading.Thread(target=_task, daemon=True).start()

    def set_mode(self, mode: str) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/settings/mode", json={"mode": mode}, timeout=6)
        if resp.status_code != 200:
            raise APIError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def set_mode_async(self, mode: str, on_success: Callable[[Dict[str, Any]], None], on_error: Callable[[Exception], None]):
        def _task():
            try:
                data = self.set_mode(mode)
                GLib.idle_add(on_success, data)
            except Exception as exc:
                GLib.idle_add(on_error, exc)
        threading.Thread(target=_task, daemon=True).start()

    def set_serial_port(self, port: str) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/settings/serial_port", json={"serial_port": port}, timeout=6)
        if resp.status_code != 200:
            raise APIError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def set_serial_port_async(self, port: str, on_success: Callable[[Dict[str, Any]], None], on_error: Callable[[Exception], None]):
        def _task():
            try:
                data = self.set_serial_port(port)
                GLib.idle_add(on_success, data)
            except Exception as exc:
                GLib.idle_add(on_error, exc)
        threading.Thread(target=_task, daemon=True).start()

    def set_watchdog(self, enabled: bool) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/settings/watchdog", json={"watchdog": enabled}, timeout=6)
        if resp.status_code != 200:
            raise APIError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def set_watchdog_async(self, enabled: bool, on_success: Callable[[Dict[str, Any]], None], on_error: Callable[[Exception], None]):
        def _task():
            try:
                data = self.set_watchdog(enabled)
                GLib.idle_add(on_success, data)
            except Exception as exc:
                GLib.idle_add(on_error, exc)
        threading.Thread(target=_task, daemon=True).start()

# === NETWORK CLIENT ===

class NetworkAPIClient:
    """Client for network-related API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip("/")

    def get_networks(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        params = filters or {}
        resp = requests.get(f"{self.base_url}/networks", params=params, timeout=6)
        if resp.status_code != 200:
            raise APIError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def get_networks_async(self, filters: Dict[str, Any], on_success: Callable[[List[Dict[str, Any]]], None], on_error: Callable[[Exception], None]):
        def _task():
            try:
                data = self.get_networks(filters)
                GLib.idle_add(on_success, data)
            except Exception as exc:
                GLib.idle_add(on_error, exc)
        threading.Thread(target=_task, daemon=True).start()


# === NIC / Attack CLIENT ===

class AttackAPIClient:
    """Client for NIC attack operations."""

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip("/")

    def launch_attack(
        self, mode: str, target: str | None = None, channel: int | None = None
    ) -> Dict[str, Any]:
        payload = {"mode": mode, "target": target, "channel": channel}
        resp = requests.post(f"{self.base_url}/nic/attack", json=payload, timeout=6)
        if resp.status_code != 200:
            raise APIError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def launch_attack_async(
        self,
        mode: str,
        target: str | None,
        channel: int | None,
        on_success: Callable[[Dict[str, Any]], None],
        on_error: Callable[[Exception], None],
    ):
        def _task():
            try:
                data = self.launch_attack(mode, target, channel)
                GLib.idle_add(on_success, data)
            except Exception as exc:
                GLib.idle_add(on_error, exc)

        threading.Thread(target=_task, daemon=True).start()
