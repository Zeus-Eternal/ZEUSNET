#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Settings tab with mode and serial configuration."""

import gi
import logging
from typing import Optional
from serial.tools import list_ports

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from backend.services.api_client import SettingsAPIClient

logger = logging.getLogger(__name__)


class SettingsView(Gtk.Box):
    """Settings tab for controlling mode, serial port, and watchdog."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.api_client = SettingsAPIClient()

        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)

        self._build_ui()
        GLib.idle_add(self._load_settings)

    def _build_ui(self) -> None:
        """Construct UI controls."""

        # --- Mode toggle ---
        mode_box = Gtk.Box(spacing=6)
        self.mode_label = Gtk.Label(label="Mode: Unknown")
        self.mode_btn = Gtk.Button(label="Toggle Mode")
        self.mode_btn.connect("clicked", self.on_toggle_mode)
        mode_box.append(self.mode_label)
        mode_box.append(self.mode_btn)

        # --- Serial port selector ---
        port_box = Gtk.Box(spacing=6)
        self.port_combo = Gtk.ComboBoxText()
        self.port_combo.connect("changed", self.on_port_selected)
        self._populate_ports()
        port_box.append(Gtk.Label(label="Serial Port:"))
        port_box.append(self.port_combo)

        # --- Aggressive watchdog toggle ---
        watchdog_box = Gtk.Box(spacing=6)
        self.watchdog_switch = Gtk.Switch()
        self.watchdog_switch.connect("notify::active", self.on_watchdog_toggled)
        watchdog_box.append(Gtk.Label(label="Aggressive Watchdog:"))
        watchdog_box.append(self.watchdog_switch)

        # --- Assemble ---
        self.append(mode_box)
        self.append(port_box)
        self.append(watchdog_box)
        self.append(self.status_label)

    def _populate_ports(self) -> None:
        self.port_combo.remove_all()
        ports = [p.device for p in list_ports.comports()]
        for port in ports:
            self.port_combo.append_text(port)
        if ports:
            self.port_combo.set_active(0)

    def _load_settings(self) -> bool:
        self.status_label.set_text("Loading settings...")

        def _on_success(data: dict) -> None:
            mode = data.get("mode", "Unknown")
            self.mode_label.set_text(f"Mode: {mode}")
            current_port = data.get("serial_port")
            watchdog = data.get("watchdog", False)
            self.watchdog_switch.set_active(bool(watchdog))
            self._populate_ports()
            if current_port:
                ports = [p.device for p in list_ports.comports()]
                if current_port in ports:
                    self.port_combo.set_active(ports.index(current_port))
            self.status_label.set_text("Settings loaded")

        def _on_error(err: Exception) -> None:
            logger.error("Settings fetch failed: %s", err)
            self.status_label.set_text("Failed to load settings")

        self.api_client.fetch_settings_async(_on_success, _on_error)
        return False

    def on_toggle_mode(self, _btn: Gtk.Button) -> None:
        current = self.mode_label.get_text()
        new_mode = "AGGRESSIVE" if "SAFE" in current else "SAFE"
        self.status_label.set_text(f"Switching to {new_mode}...")

        def _on_success(data: dict) -> None:
            self.mode_label.set_text(f"Mode: {data.get('mode', new_mode)}")
            self.status_label.set_text(f"Mode set to {new_mode}")

        def _on_error(err: Exception) -> None:
            logger.error("Mode switch failed: %s", err)
            self.status_label.set_text("Failed to set mode")

        self.api_client.set_mode_async(new_mode, _on_success, _on_error)

    def on_port_selected(self, combo: Gtk.ComboBoxText) -> None:
        port = combo.get_active_text()
        if not port:
            return
        self.status_label.set_text(f"Setting port to {port}...")

        def _on_success(_data: dict) -> None:
            self.status_label.set_text(f"Port set to {port}")

        def _on_error(err: Exception) -> None:
            logger.error("Port update failed: %s", err)
            self.status_label.set_text("Failed to set port")

        self.api_client.set_serial_port_async(port, _on_success, _on_error)

    def on_watchdog_toggled(self, _switch: Gtk.Switch, _param) -> None:
        enabled = self.watchdog_switch.get_active()
        self.status_label.set_text("Updating watchdog...")

        def _on_success(_data: dict) -> None:
            state = "enabled" if enabled else "disabled"
            self.status_label.set_text(f"Watchdog {state}")

        def _on_error(err: Exception) -> None:
            logger.error("Watchdog update failed: %s", err)
            self.status_label.set_text("Failed to update watchdog")

        self.api_client.set_watchdog_async(enabled, _on_success, _on_error)
