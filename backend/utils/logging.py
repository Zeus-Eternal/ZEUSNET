"""Logging utilities for the ZeusNet backend."""

import logging


def configure_logging(level: int = logging.INFO,
                      fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s") -> None:
    """Configure the root logger."""
    logging.basicConfig(level=level, format=fmt)

