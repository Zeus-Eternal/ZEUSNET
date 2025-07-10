#!/usr/bin/env python3
"""Packet Forge tab for crafting custom packets."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

try:
    from backend.services.api_client import ForgeAPIClient
except ImportError:  # pragma: no cover - fallback when run directly
    import os
    import sys

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)
    if GRANDPARENT_DIR not in sys.path:
        sys.path.insert(0, GRANDPARENT_DIR)
    from backend.services.api_client import ForgeAPIClient


class PacketForgeView(Gtk.Box):
    """Simple UI for sending crafted packets via backend API."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        self.api_client = ForgeAPIClient()
        self._build_ui()

    def _build_ui(self) -> None:
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Frame type
        type_row = Gtk.Box(spacing=6)
        type_row.append(Gtk.Label(label="Frame Type:", xalign=0))
        self.type_entry = Gtk.Entry()
        type_row.append(self.type_entry)
        form.append(type_row)

        # Payload
        payload_row = Gtk.Box(spacing=6)
        payload_row.append(Gtk.Label(label="Payload:", xalign=0))
        self.payload_entry = Gtk.Entry()
        payload_row.append(self.payload_entry)
        form.append(payload_row)

        send_btn = Gtk.Button(label="Send Packet")
        send_btn.connect("clicked", self.on_send)
        form.append(send_btn)

        self.status_label = Gtk.Label(label="", xalign=0)
        form.append(self.status_label)

        self.append(form)

    def on_send(self, _btn: Gtk.Button) -> None:
        frame_type = self.type_entry.get_text()
        payload = self.payload_entry.get_text()
        self.status_label.set_text("Sending packet...")

        def _on_success(data: dict) -> None:
            self.status_label.set_text(data.get("status", "sent"))

        def _on_error(err: Exception) -> None:
            self.status_label.set_text(f"Error: {err}")

        self.api_client.send_packet_async(frame_type, payload, _on_success, _on_error)
