#!/usr/bin/env python3
"""ZeusNet Frontend Main Entry Point."""

import os
import sys

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib

try:  # Allow execution as a script without the -m flag
    from .app import ZeusApp
    from .utils.logging import configure_logging
except ImportError:  # pragma: no cover - fallback for direct execution
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)
    from frontend.app import ZeusApp
    from frontend.utils.logging import configure_logging


def main() -> int:
    """Application entry point."""
    configure_logging()
    gi.require_version("Gtk", "4.0")
    app = ZeusApp()
    exit_status = app.run()
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
