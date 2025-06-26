#!/usr/bin/env python3
"""ZeusNet Frontend Main Entry Point."""

import gi
from gi.repository import GLib

from .app import ZeusApp
from .utils.logging import configure_logging


def main() -> int:
    """Application entry point."""
    configure_logging()
    gi.require_version("Gtk", "4.0")
    app = ZeusApp()
    exit_status = app.run()
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
