#!/usr/bin/env python3
"""ZeusNet Frontend Main Entry Point."""

import os
import sys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib  # Include Gdk for CSS!

# --- Load CSS at the very start, before any windows are created ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(CURRENT_DIR, "style.css")  # <-- Change if your style.css is elsewhere

provider = Gtk.CssProvider()
provider.load_from_path(CSS_PATH)
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(),
    provider,
    Gtk.STYLE_PROVIDER_PRIORITY_USER,
)
# --- End CSS loader ---

try:  # Allow execution as a script without the -m flag
    from .app import ZeusApp
    from .utils.logging import configure_logging
except ImportError:  # Fallback for direct execution
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)
    from frontend.app import ZeusApp
    from frontend.utils.logging import configure_logging

def main() -> int:
    """Application entry point."""
    configure_logging()
    app = ZeusApp()
    exit_status = app.run()
    return exit_status

if __name__ == "__main__":
    raise SystemExit(main())
