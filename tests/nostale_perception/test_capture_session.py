from __future__ import annotations

import pytest

from app.nostale_perception.capture_session import capture_session


def test_capture_session_rejects_invalid_count() -> None:
    with pytest.raises(ValueError, match="positive"):
        capture_session("NosTale", "tmp", 0, hwnd=1)
