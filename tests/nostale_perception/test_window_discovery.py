from __future__ import annotations

from app.nostale_perception.window_discovery import discover_windows


def test_discovery_is_safe_and_empty_off_windows() -> None:
    import sys

    candidates = discover_windows("NosTale")
    if sys.platform != "win32":
        assert candidates == []
