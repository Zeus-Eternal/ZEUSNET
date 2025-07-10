#!/usr/bin/env python3
"""ZeusNet Frontend Main Entry Point."""

import os
import sys
import logging
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk  # Gdk needed for CSS

# --- CSS LOADER: Load custom style before any windows ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(CURRENT_DIR, "style.css")  # Adjust if needed

provider = Gtk.CssProvider()
if os.path.exists(CSS_PATH):
    provider.load_from_path(CSS_PATH)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER,
    )

def main() -> int:
    try:
        from frontend.app import ZeusApp
        from frontend.utils.logging import configure_logging
    except ImportError:
        PARENT_DIR = os.path.dirname(CURRENT_DIR)
        if PARENT_DIR not in sys.path:
            sys.path.insert(0, PARENT_DIR)
        from frontend.app import ZeusApp
        from frontend.utils.logging import configure_logging

    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Launching ZeusNet GTK Frontend...")
    app = ZeusApp()
    rc = app.run()
    logger.info("ZeusNet exited with code: %s", rc)
    return rc

if __name__ == "__main__":
    sys.exit(main())
