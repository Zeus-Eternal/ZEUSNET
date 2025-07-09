#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZeusNet GTK4 Dashboard View — Full Production Version."""

import io
import logging
from typing import List, Dict, Any, Optional
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from gi.repository import Gtk, GdkPixbuf

logger = logging.getLogger(__name__)

class DashboardView(Gtk.Box):
    """
    Dashboard panel showing stats and a live histogram chart.
    GTK4 only—uses .append(), never pack_start/pack_end.
    """

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        # Chart image (matplotlib)
        self.chart_image = Gtk.Image()
        self.append(self.chart_image)

        # Stats summary
        self.stats_label = Gtk.Label(label="Loading dashboard data...")
        self.stats_label.set_halign(Gtk.Align.START)
        self.append(self.stats_label)

    def update_dashboard(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """Update dashboard view with new data."""
        if not data:
            self.stats_label.set_text("No data available")
            self.chart_image.clear()
            return

        try:
            total = len(data)
            avg_rssi = sum(n.get("rssi", -100) for n in data) / total if total else -100
            unique_ssids = len({n.get("ssid", "Unknown") for n in data})
            secured_count = sum(1 for n in data if n.get("auth", "") != "OPEN")

            stats_summary = (
                f"Total Networks: {total} | "
                f"Avg RSSI: {avg_rssi:.1f} dBm | "
                f"Unique SSIDs: {unique_ssids} | "
                f"Secured: {secured_count}"
            )
            self.stats_label.set_text(stats_summary)
            self._draw_rssi_distribution_chart(data)
        except Exception:
            logger.exception("Dashboard update failed")
            self.stats_label.set_text("Dashboard update error")
            self.chart_image.clear()

    def _draw_rssi_distribution_chart(self, data: List[Dict[str, Any]]) -> None:
        """Draw histogram of RSSI values as a Matplotlib PNG in GTK4."""
        try:
            rssi_values = [n.get("rssi", -100) for n in data if "rssi" in n]
            if not rssi_values:
                self.chart_image.clear()
                return

            fig = Figure(figsize=(6, 3), dpi=100)
            ax = fig.add_subplot(111)
            ax.hist(rssi_values, bins=10, range=(-100, 0), color="#007acc", edgecolor="black")
            ax.set_title("Signal Strength Distribution")
            ax.set_xlabel("RSSI (dBm)")
            ax.set_ylabel("Count")
            ax.grid(True, linestyle='--', alpha=0.5)

            buf = io.BytesIO()
            FigureCanvas(fig).print_png(buf)
            loader = GdkPixbuf.PixbufLoader.new_with_type("png")
            loader.write(buf.getvalue())
            loader.close()
            pixbuf = loader.get_pixbuf()
            self.chart_image.set_from_pixbuf(pixbuf)
        except Exception:
            logger.exception("Chart rendering failed")
            self.chart_image.clear()
            self.stats_label.set_text("Chart rendering error")
