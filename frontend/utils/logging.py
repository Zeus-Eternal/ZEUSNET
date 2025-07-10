"""Logging utilities for ZeusNet frontend."""

import logging


def configure_logging(
    level: int = logging.INFO,
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """Configure the root logger.

    Parameters
    ----------
    level : int
        Logging level for root logger. Defaults to ``logging.INFO``.
    fmt : str
        Log message format.
    """
    logging.basicConfig(level=level, format=fmt)


