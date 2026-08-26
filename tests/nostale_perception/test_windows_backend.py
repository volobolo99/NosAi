from __future__ import annotations

import pytest

from app.nostale_perception.windows_backend import Win32WindowCaptureBackend


def test_win32_backend_is_platform_guarded() -> None:
    backend = Win32WindowCaptureBackend()
    if __import__("sys").platform != "win32":
        with pytest.raises((AttributeError, OSError, ValueError)):
            backend.capture(1)
