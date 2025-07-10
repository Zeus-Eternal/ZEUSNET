import os
import sys


def ensure_repo_root_on_path() -> None:
    """Add repository root to ``sys.path`` for direct script execution.

    When running modules like ``frontend/main.py`` directly, Python only adds
    the directory containing that script to ``sys.path``. Relative imports then
    fail because the package root (one level up) isn't visible. This helper
    inserts the repository root so imports work consistently.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

