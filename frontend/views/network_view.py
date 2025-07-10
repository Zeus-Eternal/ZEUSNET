#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Network tab implementation."""

import gi
import logging
from typing import Dict

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

if __package__ is None:
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from frontend.utils.path_setup import ensure_repo_root_on_path
ensure_repo_root_on_path()

from frontend.widgets.network_list import NetworkList
from backend.services.api_client import NetworkAPIClient

logger = logging.getLogger(__name__)

class NetworkView(Gtk.Box):
    """
    Displays available networks with filter controls and double-click-to-attack UX.
    Emits target info to main window/controller for prefilled attack tab.
    """
    def __init__(self, parent_controller=None) -> None:
        """
        Args:
            parent_controller: Reference to main window/controller for tab switching (optional).
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.api_client = NetworkAPIClient()
        self.parent_controller = parent_controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        # Filter Controls
        filter_box = Gtk.Box(spacing=6)
        self.filter_entry = Gtk.Entry(placeholder_text="Filter SSID")
        filter_btn = Gtk.Button(label="Apply")
        filter_btn.connect("clicked", self.on_apply_filters)
        filter_box.append(self.filter_entry)
        filter_box.append(filter_btn)

        # Network List
        self.network_list = NetworkList()
        self.network_list.connect("target-selected", self.on_target_selected)

        # Status Label
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)

        # Layout
        self.append(filter_box)
        self.append(self.network_list)
        self.append(self.status_label)

        # Initial network fetch
        GLib.idle_add(self._initial_fetch)

    def on_apply_filters(self, _button: Gtk.Button) -> None:
        filters = {"ssid": self.filter_entry.get_text()}
        self._refresh_networks(filters)

    def _initial_fetch(self) -> bool:
        self._refresh_networks({})
        return False

    def _refresh_networks(self, filters: Dict[str, str]) -> None:
        self.status_label.set_text("Loading networks...")
        self.network_list.set_loading_state(True)

        def _on_success(data):
            self.network_list.set_loading_state(False)
            self.network_list.load_data(data)
            self.status_label.set_text(f"{len(data)} networks loaded")

        def _on_error(error):
            logger.error("Failed to fetch networks: %s", error)
            self.network_list.set_loading_state(False)
            self.status_label.set_text("Failed to load networks")

        self.api_client.get_networks_async(
            filters=filters,
            on_success=_on_success,
            on_error=_on_error
        )

    def on_target_selected(self, widget, net_info):
        logger.info(f"Target selected: {net_info}")
        # Use parent_controller if present, else root
        if self.parent_controller and hasattr(self.parent_controller, "switch_to_attack_tab"):
            self.parent_controller.switch_to_attack_tab(net_info)
        else:
            root = self.get_root()
            if root and hasattr(root, "switch_to_attack_tab"):
                root.switch_to_attack_tab(net_info)
            else:
                logger.warning("No attack tab handler found for double-click target event.")
