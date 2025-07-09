#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Attack tab with prefillable target controls."""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

class AttackView(Gtk.Box):
    """
    Full-featured Attack controls tab. Accepts prefill via prefill_target(net_info).
    """

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        self._build_ui()

    def _build_ui(self):
        """Build all attack controls with labeled, editable fields."""

        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # SSID
        ssid_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        ssid_label = Gtk.Label(label="SSID:", xalign=0)
        self.ssid_entry = Gtk.Entry()
        ssid_row.append(ssid_label)
        ssid_row.append(self.ssid_entry)
        form.append(ssid_row)

        # BSSID
        bssid_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bssid_label = Gtk.Label(label="BSSID:", xalign=0)
        self.bssid_entry = Gtk.Entry()
        bssid_row.append(bssid_label)
        bssid_row.append(self.bssid_entry)
        form.append(bssid_row)

        # Channel
        channel_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        channel_label = Gtk.Label(label="Channel:", xalign=0)
        self.channel_entry = Gtk.Entry()
        channel_row.append(channel_label)
        channel_row.append(self.channel_entry)
        form.append(channel_row)

        # Encryption
        enc_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        enc_label = Gtk.Label(label="Encryption:", xalign=0)
        self.enc_entry = Gtk.Entry()
        enc_row.append(enc_label)
        enc_row.append(self.enc_entry)
        form.append(enc_row)

        # Signal Quality
        quality_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        quality_label = Gtk.Label(label="Signal Quality:", xalign=0)
        self.quality_entry = Gtk.Entry()
        quality_row.append(quality_label)
        quality_row.append(self.quality_entry)
        form.append(quality_row)

        # RSSI
        rssi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        rssi_label = Gtk.Label(label="RSSI:", xalign=0)
        self.rssi_entry = Gtk.Entry()
        rssi_row.append(rssi_label)
        rssi_row.append(self.rssi_entry)
        form.append(rssi_row)

        # Any advanced/hidden fields? Add here as needed.

        # Action buttons
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.attack_btn = Gtk.Button(label="⚡ Launch Attack")
        self.attack_btn.connect("clicked", self.on_attack_clicked)
        btn_row.append(self.attack_btn)
        form.append(btn_row)

        # Status label for UX feedback
        self.status_label = Gtk.Label(label="", xalign=0)
        form.append(self.status_label)

        self.append(form)

    def prefill_target(self, net_info):
        """Prefill all target fields from provided network info."""
        self.ssid_entry.set_text(net_info.get('ssid', ''))
        self.bssid_entry.set_text(net_info.get('bssid', ''))
        self.channel_entry.set_text(str(net_info.get('channel', '')))
        self.enc_entry.set_text(net_info.get('encryption', ''))
        self.quality_entry.set_text(str(net_info.get('quality', '')))
        self.rssi_entry.set_text(str(net_info.get('rssi', '')))
        self.status_label.set_text("Target loaded. Ready to launch your diabolical plan.")

    def on_attack_clicked(self, _btn):
        """Evil placeholder for actual attack logic."""
        ssid = self.ssid_entry.get_text()
        bssid = self.bssid_entry.get_text()
        channel = self.channel_entry.get_text()
        enc = self.enc_entry.get_text()
        quality = self.quality_entry.get_text()
        rssi = self.rssi_entry.get_text()
        # TODO: Integrate actual backend attack logic here
        self.status_label.set_text(
            f"Attack launched on SSID '{ssid}' (BSSID: {bssid}, Channel: {channel}, Encryption: {enc}, Quality: {quality}, RSSI: {rssi})"
        )

