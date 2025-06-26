"""Logging utilities for ZeusNet frontend."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger.

    Parameters
    ----------
    level : int
        Logging level for root logger. Defaults to ``logging.INFO``.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

